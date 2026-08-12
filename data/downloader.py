import time
from utils.logger import logger
from utils.validator import validate_normalize
from data.cache import load_cache, save_cache
from data.normalize import normalize_DataFrame
import yfinance as yf
import pandas as pd

def get_data(symbols: list[str], start=None, end=None, period="1y", interval="1d") -> dict[str, pd.DataFrame]:
    """
    Get historical market data, either from cache or by downloading.

    Parameters
    ----------
    symbol : list[str]
        Stock tickers (e.g. [AAPL, NVDA, etc.])
    start : datetime | None
        Start date
    end : datetime | None
        End date
    period : str
        Period if start/end are omitted
    interval : str
        Data interval

    Returns
    -------
    pd.DataFrame
        Historical OHLCV data
    """

    data = {}
    
    for symbol in symbols:
        symbol, start, end, period, interval = validate_normalize(symbol, start, end, period, interval)
    
        df = load_cache(symbol, period, interval)
    
        if df is not None:
            data[symbol] = df
            continue
        
        df = download_data(symbol, start=start, end=end, period=period, interval=interval)
        
        df = normalize_DataFrame(df)
        
        if not save_cache(symbol, period, interval, df):
            logger.warning("Failed to save cache for %s", symbol)

        data[symbol] = df

    return data

def download_data(symbol: str, start=None, end=None, period="1y", interval="1d") -> pd.DataFrame:
    """
    Download historical market data.

    Parameters
    ----------
    symbol : str
        Stock ticker (e.g. AAPL)
    start : datetime | None
        Start date
    end : datetime | None
        End date
    period : str
        Period if start/end are omitted
    interval : str
        Data interval

    Returns
    -------
    pd.DataFrame
        Historical OHLCV data
    """

    start_time = time.perf_counter()

    try:
        logger.info("Downloading data for %s", symbol)
        df = yf.download(symbol, start=start, end=end, period=period, interval=interval)
        
        elapsed_time = time.perf_counter() - start_time

        logger.info("Downloaded %d rows for %s in %.2f seconds", len(df), symbol, elapsed_time)
    except Exception as e:
        logger.exception("Error occurred while downloading data for %s: %s", symbol, e)
        raise
    
    if df.empty:
        logger.critical("No data found for %s.", symbol)
        raise RuntimeError(f"No market data returned for {symbol}.")

    return df
