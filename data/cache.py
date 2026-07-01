import pandas as pd

from utils.logger import logger
from time import time
from config import CACHE_DIR

def get_cache_path(symbol: str, period: str, interval: str) -> str:
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
    str
        Path to the cache file
    """

    logger.info("Getting cache path for %s with period %s and interval %s.", symbol, period, interval)

    return CACHE_DIR / "%s_%s_%s.csv" % (symbol, period, interval)

def is_cache_valid(symbol: str, period: str, interval: str) -> bool:
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
        logger.info("Found cache file for %s with period %s and interval %s.", symbol, period, interval)
        return True
    else:
        logger.warning("Could not find cache file or file is empty for %s with period %s and interval %s.", symbol, period, interval)
        return False
     

def load_cache(symbol: str, period: str, interval: str) -> pd.DataFrame:
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
    pd.DataFrame
        Cached historical OHLCV data
    """

    cache_path = get_cache_path(symbol, period, interval)
    
    if not cache_path.exists():
        logger.warning("Cache file not found for %s with period %s and interval %s.", symbol, period, interval)
        raise FileNotFoundError("Cache file not found for %s with period %s and interval %s." % (symbol, period, interval))
    else:
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        logger.info("Loaded %d rows.", df.shape[0])
        return df

def save_cache(symbol: str, period: str, interval: str, df: pd.DataFrame) -> None:
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
    """

    cache_path = get_cache_path(symbol, period, interval)
    
    logger.info("Saving cache")

    df.to_csv(cache_path)

    if cache_path.exists() and cache_path.stat().st_size > 0:
        test = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if len(test) == len(df):
            logger.info("Saved cache %s (%d rows, %d)", cache_path, df.shape[0], cache_path.stat().st_size)
            return True
        else:
            logger.warning("Failed to save cache for %s with period %s and interval %s.", symbol, period, interval)
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

    cache_path = get_cache_path(symbol, period, interval)
    
    if not cache_path.exists():
        logger.warning("Cache file not found for %s with period %s and interval %s.", symbol, period, interval)
        return False
    
    age = time.time() - cache_path.stat().st_mtime
    if age < max_age_hours * 3600:
        logger.info("Cache file is recent for %s with period %s and interval %s.", symbol, period, interval)
        return True
    else:
        logger.warning("Cache file is not recent for %s with period %s and interval %s.", symbol, period, interval)
        return False