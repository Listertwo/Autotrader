#imports
import pandas as pd
import numpy as np
from utils.logger import logger

#Helper Functions
def _validate_inputs(df: pd.DataFrame, period: int, column: str) -> pd.DataFrame:
	"""Validates inputs before adding any indicators to DataFrames.

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

	df = df.copy()

	return df

def _group_by_date(df: pd.DataFrame, frequency: str = "D") -> pd.Series:
	"""
	Groups a DataFrame by date.

	Parameters
	----------
	df : pd.DataFrame
		Historical market data.

	frequency : str
		Frequency for grouping (e.g., 'D' for daily, 'W' for weekly).

	Returns
	-------
	pd.Series
		A Series with the date as the index and the group number as the values.
	"""

	if not isinstance(df.index, pd.DatetimeIndex):
		raise TypeError("DataFrame index must be a DatetimeIndex")

	return df.index.floor(frequency)

#Moving Averages
def add_sma(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Simple Moving Average (SMA) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the SMA.
	
	column : str, default="Close"
	    Column on which to calculate the SMA.
	
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
	    Number of periods used to calculate the WMA.
	
	column : str, default="Close"
	    Column on which to calculate the WMA.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    WMA_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)

	weights = np.arange(1, period + 1)
	df[f"WMA_{period}_{column}"] = (df[column].rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True))

	return df
	
#Returns
def add_returns(df: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
	"""
	Add a simple returns indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	column : str, default="Close"
	    Column on which to calculate the returns.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    Returns_<column> column.
	"""

	df = _validate_inputs(df, 1, column)
	
	df[f"Returns_{column}"] = (df[column].pct_change())
	
	return df

def add_log_returns(df: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
	"""
	Add a log returns indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	column : str, default="Close"
	    Column on which to calculate the log returns.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    Log_Returns_<column> column.
	"""

	df = _validate_inputs(df, 1, column)
	
	df[f"Log_Returns_{column}"] = (np.log(df[column] / df[column].shift(1)))
	
	return df

#Volatility
def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
	"""
	Add an Average True Range (ATR) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int, default=14
	    Number of periods used to calculate the ATR.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    ATR_<period> column.
	"""

	df = _validate_inputs(df, period, "Close")
	
	df["H-L"] = df["High"] - df["Low"]
	df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
	df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
	df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
	df[f"ATR_{period}"] = df["TR"].ewm(alpha=1/period, adjust=False, min_periods=period).mean()
	
	df.drop(columns=["H-L", "H-PC", "L-PC", "TR"], inplace=True)
	
	return df

def add_stddev(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Standard Deviation (STDDEV) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the STDDEV.
	
	column : str, default="Close"
	    Column on which to calculate the STDDEV.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    STDDEV_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	df[f"STDDEV_{period}_{column}"] = (df[column].rolling(window=period).std())
	
	return df

#Volume
def add_volume_sma(df: pd.DataFrame, period: int) -> pd.DataFrame:
	"""
	Add a Simple Moving Average (SMA) of volume indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the SMA of volume.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    Volume_SMA_<period> column.
	"""

	df = _validate_inputs(df, period, "Volume")
	
	df[f"Volume_SMA_{period}"] = (df["Volume"].rolling(window=period).mean())

	return df

def add_vwap(df: pd.DataFrame, reset_daily: bool = False) -> pd.DataFrame:
	"""
	Add a Volume Weighted Average Price (VWAP) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	reset_daily : bool, default=False
	    Whether to reset the cumulative calculations at the beginning of each day.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    VWAP column.
	"""

	df = _validate_inputs(df, 1, "Close")
	
	if reset_daily and not isinstance(df.index, pd.DatetimeIndex):
		raise TypeError("reset_daily is True, but the DataFrame index is not a DatetimeIndex")

	tp = (df["High"] + df["Low"] + df["Close"]) / 3
	tpv = tp * df["Volume"]

	if reset_daily:
		daily_group = _group_by_date(df)
		cumulative_tpv = tpv.groupby(daily_group).cumsum()
		cumulative_volume = df["Volume"].groupby(daily_group).cumsum()
		df["VWAP_Daily"] = cumulative_tpv / cumulative_volume
	else:
		cumulative_tpv = tpv.cumsum()
		cumulative_volume = df["Volume"].cumsum()
		df["VWAP"] = cumulative_tpv / cumulative_volume
		
	return df

#Rolling Statistics
def add_highest(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Highest High (HH) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the HH.
	
	column : str, default="Close"
	    Column on which to calculate the HH.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    HH_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	df[f"HH_{period}_{column}"] = (df[column].rolling(window=period).max())
	
	return df

def add_lowest(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Lowest Low (LL) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the LL.
	
	column : str, default="Close"
	    Column on which to calculate the LL.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    LL_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	df[f"LL_{period}_{column}"] = (df[column].rolling(window=period).min())
	
	return df

def add_range(df: pd.DataFrame, period: int, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Range (RANGE) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int
	    Number of periods used to calculate the RANGE.
	
	column : str, default="Close"
	    Column on which to calculate the RANGE.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    RANGE_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	df[f"RANGE_{period}_{column}"] = (df[column].rolling(window=period).max() - df[column].rolling(window=period).min())

	return df

#Momentum
def add_rsi(df: pd.DataFrame, period: int = 14, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Relative Strength Index (RSI) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int, default=14
	    Number of periods used to calculate the RSI.
	
	column : str, default="Close"
	    Column on which to calculate the RSI.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with an additional
	    RSI_<period>_<column> column.
	"""

	df = _validate_inputs(df, period, column)
	
	delta = df[column].diff()
	gain = delta.clip(lower=0)
	loss = (-delta).clip(lower=0)

	avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
	avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()

	rs = avg_gain / avg_loss
	df[f"RSI_{period}_{column}"] = 100 - (100 / (1 + rs))

	return df

def add_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, column: str = "Close") -> pd.DataFrame:
	"""
	Add a Moving Average Convergence Divergence (MACD) indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	fast_period : int, default=12
	    Number of periods used to calculate the fast EMA.
	
	slow_period : int, default=26
	    Number of periods used to calculate the slow EMA.
	
	signal_period : int, default=9
	    Number of periods used to calculate the signal line.
	
	column : str, default="Close"
	    Column on which to calculate the MACD.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with additional
	    MACD_f{fast_period}_s{slow_period}_g{signal_period}_{column},
	    MACD_Signal_f{fast_period}_s{slow_period}_g{signal_period}_{column},
	    and MACD_Histogram_f{fast_period}_s{slow_period}_g{signal_period}_{column}
	    columns.
	"""

	df = _validate_inputs(df, slow_period, column)

	if not isinstance(fast_period, int) or not isinstance(slow_period, int) or not isinstance(signal_period, int):
		raise TypeError("fast_period, slow_period, and signal_period must be integers")
	if fast_period <= 0 or slow_period <= 0 or signal_period <= 0:
		raise ValueError("fast_period, slow_period, and signal_period must be greater than zero")
	
	fast_ema = df[column].ewm(alpha=1/fast_period, adjust=False, min_periods=fast_period).mean()
	slow_ema = df[column].ewm(alpha=1/slow_period, adjust=False, min_periods=slow_period).mean()
	macd = fast_ema - slow_ema
	signal = macd.ewm(span=signal_period, adjust=False).mean()
	histogram = macd - signal

	df[f"MACD_f{fast_period}_s{slow_period}_g{signal_period}_{column}"] = macd
	df[f"MACD_Signal_f{fast_period}_s{slow_period}_g{signal_period}_{column}"] = signal
	df[f"MACD_Histogram_f{fast_period}_s{slow_period}_g{signal_period}_{column}"] = histogram

	return df

def add_stochastic(df: pd.DataFrame, period: int = 14, smooth: int = 3) -> pd.DataFrame:
	"""
	Add a Stochastic Oscillator indicator to a DataFrame.
	
	Parameters
	----------
	df : pd.DataFrame
	    Historical market data.
	
	period : int, default=14
	    Number of periods used to calculate the %K line.
	
	smooth : int, default=3
	    Number of periods used to smooth the %K line.
	
	Returns
	-------
	pd.DataFrame
	    A copy of the input DataFrame with additional
	    Stochastic_%K_<period>_<smooth> and Stochastic_%D_<period>_<smooth>
	    columns.
	"""

	df = _validate_inputs(df, period, "Close")

	if not isinstance(smooth, int):
		raise TypeError("smooth must be an integer")
	
	df = add_highest(df, period, "High")
	df = add_lowest(df, period, "Low")
	
	lowest = df[f"LL_{period}_Low"]
	highest = df[f"HH_{period}_High"]
	
	k = 100 * (df["Close"] - lowest) / (highest - lowest)
	d = k.rolling(window=smooth).mean()

	df[f"Stochastic_%K_{period}_{smooth}"] = k
	df[f"Stochastic_%D_{period}_{smooth}"] = d

	return df
