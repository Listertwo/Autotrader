import pandas as pd
from pathlib import Path

from utils.logger import logger
from utils.validator import validate_normalize
import time
from config import CACHE_DIR

def get_cache_path(symbol: str, period: str, interval: str) -> Path:
    """
    Get the path to the cache file.

    symbol : str
        Stock ticker (e.g. AAPL)
    period : str
        Time period (e.g. 1d, 5d, 1mo)
    interval : str
        Data interval (e.g. 1h, 1d)
    Returns
    -------
    Path
        Path to the cache file
    """
        
    logger.info("Getting cache path for %s_%s_%s.csv", symbol, period, interval)
    if not CACHE_DIR.exists():
        logger.info("CACHE_DIR does not exist. Creating cache directory %s", CACHE_DIR)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    return CACHE_DIR / f"{symbol}_{period}_{interval}.csv"

def has_cache(symbol: str, period: str, interval: str) -> bool:
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

    Returns
    -------
    bool
        True if the cache file exists and is valid, False otherwise
    """

    cache_path = get_cache_path(symbol, period, interval)

    if cache_path.exists() and cache_path.stat().st_size > 0:
        logger.info("Found cache file for %s_%s_%s.csv", symbol, period, interval)
        return True
    else:
        logger.warning("Could not find cache file or file is not valid for %s_%s_%s.csv", symbol, period, interval)
        return False
     

def load_cache(symbol: str, period: str, interval: str) -> pd.DataFrame | None:
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

    Returns
    -------
    pd.DataFrame | None
        Cached historical OHLCV data or None if loading fails
    """

    cache_path = get_cache_path(symbol, period, interval)
    
    if is_cache_recent(symbol, period, interval):
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

def save_cache(symbol: str, period: str, interval: str, df: pd.DataFrame) -> bool:
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
    
    Returns
    -------
    bool
        True if the cache file was saved successfully, False otherwise
    """

    cache_path = get_cache_path(symbol, period, interval)
    
    logger.info("Saving cache")
    try:
        df.to_csv(cache_path)
    except Exception as e:
        logger.exception("Error occurred while saving cache: %s", e)
        return False

    if has_cache(symbol, period, interval):
        try:
            test = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        except Exception as e:
            logger.exception("Error occurred while reading back the cache file: %s", e)
            return False

        if test.shape == df.shape:
            logger.info("Saved cache %s (%d rows, %d)", cache_path, df.shape[0], cache_path.stat().st_size)
            return True
        else:
            logger.warning("Failed to save cache for %s_%s_%s.csv", symbol, period, interval)
            return False
    else:
        return False

def is_cache_recent(symbol: str, period: str, interval: str, max_age_hours: int = 24) -> bool:
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

    Returns
    -------
    bool
        True if the cache file is recent, False otherwise
    """

    if not has_cache(symbol, period, interval):
        return False

    cache_path = get_cache_path(symbol, period, interval)
    
    age = time.time() - cache_path.stat().st_mtime
    if age < max_age_hours * 3600:
        logger.info("Cache file is recent for %s_%s_%s.csv", symbol, period, interval)
        return True
    else:
        logger.warning("Cache file is not recent for %s_%s_%s.csv", symbol, period, interval)
        return False
