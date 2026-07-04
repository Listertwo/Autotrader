#imports
import pandas as pd
from utils.logger import logger

"""
Moving Averages
----------------
add_sma()
add_ema()
add_wma()

Returns
-------
add_returns()
add_log_returns()

Volatility
----------
add_atr()
add_stddev()

Volume
------
add_volume_sma()
add_vwap()

Rolling Statistics
------------------
add_highest()
add_lowest()
add_range()

Momentum
--------
add_rsi()
add_macd()
add_stochastic()
"""

#Helper Functions
def _validate_inputs(df: pd.DataFrame, period: int, column: str) -> pd.DataFrame:
	"""
	Validates inputs before adding any indicators to DataFrames.

	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the indicators.
	
	column : str
	    Column on which to calculate the indicators.

	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with validated inputs.
	"""

	df = df.copy()

	if not isinstance(df, pd.DataFrame):
		raise TypeError("df must be a pandas DataFrame")
	if not isinstance(period, int):
    	raise TypeError("period must be an integer")
	if period <= 0:
    	raise ValueError("period must be greater than zero")
	if not isinstance(column, str):
		raise TypeError("column must be a string")
	if column not in df.columns:
    	raise ValueError(f"DataFrame must contain a '{column}' column")

	return df

#Moving Averages
def add_sma(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Simple Moving Average (SMA) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the EMA.
	
	column : str, default="Close"
	    Column on which to calculate the EMA.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    SMA_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	if period > len(df):
		logger.warning("Period (%d) is greater than dataframe length (%d)", period, len(df))
	
	df[f"SMA_{period}_{column}"] = (df[column].rolling(window=period).mean())
	
	return df

def add_ema(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add an Exponential Moving Average (EMA) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the EMA.
	
	column : str, default="Close"
	    Column on which to calculate the EMA.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    EMA_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	df[f"EMA_{period}_{column}"] = (df[column].ewm(span=period, adjust=False, min_periods=period).mean())
	
	return df

def add_wma(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add an Weighted Moving Average (WMA) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the EMA.
	
	column : str, default="Close"
	    Column on which to calculate the EMA.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    WMA_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)

	df[f"WMA_{period}_{column}"] = 
	
