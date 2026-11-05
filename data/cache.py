import pandas as pd
from datetime import datetime
from pathlib import Path

from utils.logger import logger
from utils.validator import validate_normalize
import time
from config import CACHE_DIR

def _format_bound(value: datetime | None, missing: str) -> str:
    """
    Turn a start/end bound into text that is safe to use in a file name.

    Midnight dates become YYYY-MM-DD. Dates with a time (intraday requests) become
    YYYY-MM-DDTHHMM, because ':' is not allowed in Windows file names.
    """

    if value is None:
        return missing

    if value.hour == 0 and value.minute == 0 and value.second == 0 and value.microsecond == 0:
        return value.strftime("%Y-%m-%d")

    return value.strftime("%Y-%m-%dT%H%M")

def get_cache_name(symbol: str, period: str, interval: str, start: datetime | None = None, end: datetime | None = None) -> str:
    """
    Build the cache file name for one data request.

    A request is described either by a period ("1y") or by a start/end date range. When a start or
    end is given, yfinance ignores the period, so the period is left out of the name and the dates
    are used instead. This keeps two different requests from sharing (and overwriting) one file.

    Examples
    --------
    AAPL_1y_1d.csv                      period-based request
    AAPL_2020-01-01_2020-12-31_1d.csv   date-range request
    AAPL_2020-01-01_latest_1d.csv       start given, no end
    AAPL_begin_2020-12-31_1d.csv        end given, no start
    """

    if start is None and end is None:
        return f"{symbol}_{period}_{interval}.csv"

    return f"{symbol}_{_format_bound(start, 'begin')}_{_format_bound(end, 'latest')}_{interval}.csv"

def get_cache_path(symbol: str, period: str, interval: str, start: datetime | None = None, end: datetime | None = None) -> Path:
    """
    Get the path to the cache file.

    symbol : str
        Stock ticker (e.g. AAPL)
    period : str
        Time period (e.g. 1d, 5d, 1mo). Ignored when start or end is given.
    interval : str
        Data interval (e.g. 1h, 1d)
    start : datetime | None
        Start date of a date-range request
    end : datetime | None
        End date of a date-range request
    Returns
    -------
    Path
        Path to the cache file
    """

    name = get_cache_name(symbol, period, interval, start, end)

    logger.info("Getting cache path for %s", name)
    if not CACHE_DIR.exists():
        logger.info("CACHE_DIR does not exist. Creating cache directory %s", CACHE_DIR)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    return CACHE_DIR / name

def has_cache(symbol: str, period: str, interval: str, start: datetime | None = None, end: datetime | None = None) -> bool:
    """
    Check if the cache file exists and is valid.

    Parameters
    ----------
    symbol : str
        Stock ticker (e.g. AAPL)
    period : str
        Time period (e.g. 1d, 5d, 1mo)
    interval : str
        Data interval (e.g. 1h, 1d)
    start : datetime | None
        Start date of a date-range request
    end : datetime | None
        End date of a date-range request

    Returns
    -------
    bool
        True if the cache file exists and is valid, False otherwise
    """

    cache_path = get_cache_path(symbol, period, interval, start, end)

    if cache_path.exists() and cache_path.stat().st_size > 0:
        logger.info("Found cache file %s", cache_path.name)
        return True
    else:
        logger.warning("Could not find cache file or file is not valid: %s", cache_path.name)
        return False
     

def load_cache(symbol: str, period: str, interval: str, start: datetime | None = None, end: datetime | None = None) -> pd.DataFrame | None:
    """
    Load cached data from the cache file.

    Parameters
    ----------
    symbol : str
        Stock ticker (e.g. AAPL)
    period : str
        Time period (e.g. 1d, 5d, 1mo)
    interval : str
        Data interval (e.g. 1h, 1d)
    start : datetime | None
        Start date of a date-range request
    end : datetime | None
        End date of a date-range request

    Returns
    -------
    pd.DataFrame | None
        Cached historical OHLCV data or None if loading fails
    """

    cache_path = get_cache_path(symbol, period, interval, start, end)
    
    if is_cache_recent(symbol, period, interval, start=start, end=end):
        try:
            df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            logger.info("Loaded %d rows.", df.shape[0])
            return df
        except Exception as e:
            logger.exception("Error occurred while loading cache: %s", e)
            cache_path.unlink(missing_ok=True)
            return None
    else:    
        return None

def save_cache(symbol: str, period: str, interval: str, df: pd.DataFrame, start: datetime | None = None, end: datetime | None = None) -> bool:
    """
    Save data to the cache file.

    Parameters
    ----------
    symbol : str
        Stock ticker (e.g. AAPL)
    period : str
        Time period (e.g. 1d, 5d, 1mo)
    interval : str
        Data interval (e.g. 1h, 1d)
    df : pd.DataFrame
        Historical OHLCV data to be cached
    start : datetime | None
        Start date of a date-range request
    end : datetime | None
        End date of a date-range request
    
    Returns
    -------
    bool
        True if the cache file was saved successfully, False otherwise
    """

    cache_path = get_cache_path(symbol, period, interval, start, end)
    
    logger.info("Saving cache")
    try:
        df.to_csv(cache_path)
    except Exception as e:
        logger.exception("Error occurred while saving cache: %s", e)
        return False

    if has_cache(symbol, period, interval, start, end):
        try:
            test = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        except Exception as e:
            logger.exception("Error occurred while reading back the cache file: %s", e)
            return False

        if test.shape == df.shape:
            logger.info("Saved cache %s (%d rows, %d)", cache_path, df.shape[0], cache_path.stat().st_size)
            return True
        else:
            logger.warning("Failed to save cache %s", cache_path.name)
            return False
    else:
        return False

def is_cache_recent(symbol: str, period: str, interval: str, max_age_hours: int = 24, start: datetime | None = None, end: datetime | None = None) -> bool:
    """
    Check if the cache file is recent.

    Parameters
    ----------
    symbol : str
        Stock ticker (e.g. AAPL)
    period : str
        Time period (e.g. 1d, 5d, 1mo)
    interval : str
        Data interval (e.g. 1h, 1d)
    max_age_hours : int
        Maximum age of the cache file in hours
    start : datetime | None
        Start date of a date-range request
    end : datetime | None
        End date of a date-range request

    Returns
    -------
    bool
        True if the cache file is recent, False otherwise
    """

    if not has_cache(symbol, period, interval, start, end):
        return False

    cache_path = get_cache_path(symbol, period, interval, start, end)
    
    age = time.time() - cache_path.stat().st_mtime
    if age < max_age_hours * 3600:
        logger.info("Cache file is recent: %s", cache_path.name)
        return True
    else:
        logger.warning("Cache file is not recent: %s", cache_path.name)
        return False
