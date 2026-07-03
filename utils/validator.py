from datetime import datetime
from config import VALID_PERIODS, VALID_INTERVALS
from utils.logger import logger

def validate_normalize(symbol: str, start: datetime | None, end: datetime | None, period: str, interval: str) -> tuple[str, datetime | None, datetime | None, str, str]:
    """
    Validates and normalizes the data passed into the cache functions.

    Parameters
    ----------
    symbol
        Stock ticker (e.g. AAPL): str
    start
        Start date: datetime | None
    end
        End date: datetime | None
    period
        Time period (e.g. 1d, 5d, 1mo): str
    interval
        Data interval (e.g. 1h, 1d): str
    """

    logger.info("Validating variable data. Modifying data, if necessary.")

    #Validating Types
    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string.")
    
    if start is not None and not isinstance(start, datetime):
        raise TypeError("start date must be a datetime or empty")
        
    if end is not None and not isinstance(end, datetime):
        raise TypeError("end date must be a datetime or empty")

    if not isinstance(period, str):
        raise TypeError("period must be a string.")
    
    if not isinstance(interval, str):
        raise TypeError("interval must be a string.")
        
    #Normalizing data
    symbol = symbol.strip().upper()
    period = period.strip().lower()
    interval = interval.strip().lower()

    #Validating Values
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
        
    if start and end and start > end:
        raise ValueError("start date must be before end date")

    if period not in VALID_PERIODS:
        raise ValueError(
            f"unsupported period: '{period}'. "
            f"Expected one of: {sorted(VALID_PERIODS)}"
            )
    
    if interval not in VALID_INTERVALS:
        raise ValueError(
            f"unsupported interval: '{interval}'. "
            f"Expected one of: {sorted(VALID_INTERVALS)}"
            )

    print(symbol, start, end, period, interval)

    return symbol, start, end, period, interval
