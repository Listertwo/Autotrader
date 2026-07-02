import time
from utils.logger import logger
from data.cache import load_cache, save_cache, is_cache_valid
import yfinance as yf
import pandas as pd

start_time = time.perf_counter()

def download_data(symbol: str, start=None, end=None, period="1y", interval="1d") -> pd.DataFrame:
    """
    Download historical market data.

    Parameters
    ----------
    symbol : str
        Stock ticker (e.g. AAPL)
    start : datetime | str | None
        Start date
    end : datetime | str | None
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
    if is_cache_valid(symbol, start, end, period, interval):
        logger.info("Loading data from cache.")
        return load_cache(symbol, period, interval)
    else:
        logger.info("No valid cache found. Downloading data from Yahoo Finance.")
        try:
            logger.info("Downloading data for %s", symbol)
            df = yf.download(symbol, start=start, end=end, period=period, interval=interval)
            
            elapsed_time = time.perf_counter() - start_time

            logger.info("Data downloaded %d rows for %s in %.2f seconds", len(df), symbol, elapsed_time)

            if not save_cache(symbol, period, interval, df):
                logger.warning("Failed to save cache for %s_%s_%s.csv", symbol, period, interval)
        except Exception as e:
            logger.exception("Error occurred while downloading data for %s: %s", symbol, e)
            raise
    
    if df.empty:
        logger.warning("No data found for %s.", symbol)

    return df