import pandas as pd

from base import Strategy
from indicators.basic import add_rsi, add_macd, add_stochastic
from strategies.utils import cross_under, cross_over, cross_under_level, cross_over_level

class BaseRsiStrategy(Strategy):
	"""
	A relative strength index momentum strategy.
	"""

	def __init__(self, name: str, period: int = 14, oversold: int = 30, overbought: int = 70):
		super().__init__(name)
		self.period = period
		self.oversold = oversold
		self.overbought = overbought

		if not isinstance(self.period, int) or not isinstance(self.oversold, int) or not isinstance(self.overbought, int):
			raise TypeError("period, oversold, and overbought must all be positive integers")
		if self.oversold >= self.overbought:
			raise ValueError("the oversold level must be lower than the overbought level")
		if self.oversold <= 0 or self.overbought <= 0 or self.period <= 0:
			raise ValueError("the oversold, overbought, and period values must all be positive integers")

	def _prepare_rsi(self, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
		"""
		Prepare the DataFrame by adding the RSI column if it doesn't exist.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.
		period : int
			The period for calculating the RSI.

		Returns
		-------
		pd.DataFrame
			DataFrame with the RSI column added.
		"""
		
		column_name = f"RSI_{self.period}_Close"
		
		if column_name not in df.columns:
			df = add_rsi(df, self.period)
		
		return df, column_name

class RsiStrategy(BaseRsiStrategy):
	"""
	A relative stregnth index momentum strategy.
	"""

	def __init__(self, period=14, oversold=30, overbought=70):
		super().__init__("RSI", period, oversold, overbought)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
        Generate trading signals based on strength index momentum.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        pd.DataFrame
            DataFrame with trading signals.
        """

		df, column_name = self._prepare_rsi(df)

		buy = cross_over_level(df[column_name], self.oversold)
		sell = cross_under_level(df[column_name], self.overbought)

		return self.apply_signals(df, buy, sell)

class RsiCenterlineStrategy(BaseRsiStrategy):
	"""
	A relative stregnth index momentum strategy based on the centerline.
	"""
	def __init__(self, period: int = 14):
		super().__init__("RSICenterline")
		self.period = period
		self.level = 50

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
        Generate trading signals based on strength index momentum based on the centerline.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        pd.DataFrame
            DataFrame with trading signals.
        """

		df, column_name = self._prepare_rsi(df)
		
		buy = cross_over_level(df[column_name], self.level)
		sell = cross_under_level(df[column_name], self.level)

		return self.apply_signals(df, buy, sell)

class BaseMacdStrategy(Strategy):
	def __init__(self, name: str, fast: int = 12, slow: int = 26, signal: int = 9):
		super().__init__(name)
		self.fast = fast
		self.slow = slow
		self.signal = signal

		if not isinstance(self.fast, int) or not isinstance(self.slow, int) or not isinstance(self.signal, int):
			raise TypeError("fast, slow, and signal must all be positive integers")
		if self.fast <= 0 or self.slow <= 0 or self.signal <= 0:
			raise ValueError("fast, slow, and signal must all be positive integers")
		if self.fast >= self.slow:
			raise ValueError("the fast period must be lower than the slow period")
	
	def _prepare_macd(self, df: pd.DataFrame) -> tuple[pd.DataFrame, str, str, str]:
		"""
		Prepare the DataFrame by adding the MACD and signal columns if they don't exist.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.
		fast : int
			The fast period for calculating the MACD.
		slow : int
			The slow period for calculating the MACD.
		signal : int
			The signal period for calculating the MACD.

		Returns
		-------
		pd.DataFrame
			DataFrame with the MACD and signal columns added.
		"""
		
		macd_column = f"MACD_f{self.fast}_s{self.slow}_g{self.signal}_Close"
		signal_column = f"MACD_Signal_f{self.fast}_s{self.slow}_g{self.signal}_Close"
		histogram_column = f"MACD_Histogram_f{self.fast}_s{self.slow}_g{self.signal}_Close"
		
		if macd_column not in df.columns or signal_column not in df.columns or histogram_column not in df.columns:
			df = add_macd(df, self.fast, self.slow, self.signal)
		return df, macd_column, signal_column, histogram_column

class MacdStrategy(BaseMacdStrategy):
	"""
	A moving average convergence divergence momentum strategy.
	"""

	def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
		super().__init__("MACD", fast, slow, signal)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on moving average convergence divergence momentum.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, macd, signal, hist = self._prepare_macd(df)

		buy = cross_over(df[macd], df[signal])
		sell = cross_under(df[macd], df[signal])

		return self.apply_signals(df, buy, sell)
	
class MacdZeroLineStrategy(BaseMacdStrategy):
	"""
	A moving average convergence divergence momentum strategy based on the zero line.
	"""

	def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
		super().__init__("MACDZeroLine", fast, slow, signal)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on moving average convergence divergence momentum based on the zero line.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, macd, signal, hist = self._prepare_macd(df)

		buy = cross_over_level(df[macd], 0)
		sell = cross_under_level(df[macd], 0)

		return self.apply_signals(df, buy, sell)
	
class MacdHistogramStrategy(BaseMacdStrategy):
	"""
	A moving average convergence divergence momentum strategy based on the histogram.
	"""

	def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
		super().__init__("MACDHistogram", fast, slow, signal)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on moving average convergence divergence momentum based on the histogram.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, macd, signal, hist = self._prepare_macd(df)
		
		buy = cross_over_level(df[hist], 0)
		sell = cross_under_level(df[hist], 0)

		return self.apply_signals(df, buy, sell)

class BaseStochasticStrategy(Strategy):
	"""
	A base class for stochastic momentum strategies.
	"""

	def __init__(self, name: str, k_period: int = 14, d_period: int = 3):
		super().__init__(name)
		self.k_period = k_period
		self.d_period = d_period

		if not isinstance(self.k_period, int) or not isinstance(self.d_period, int):
			raise TypeError("k_period and d_period must both be positive integers")
		if self.k_period <= 0 or self.d_period <= 0:
			raise ValueError("k_period and d_period must both be positive integers")

	def _prepare_stochastic(self, df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
		"""
		Prepare the DataFrame by adding the stochastic %K and %D columns if they don't exist.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.
		k_period : int
			The period for calculating the stochastic %K.
		d_period : int
			The period for calculating the stochastic %D.

		Returns
		-------
		pd.DataFrame
			DataFrame with the stochastic %K and %D columns added.
		"""
		
		k_column = f"Stochastic_%K_{self.k_period}_Close"
		d_column = f"Stochastic_%D_{self.d_period}_Close"
		
		if k_column not in df.columns or d_column not in df.columns:
			df = add_stochastic(df, self.k_period, self.d_period)
		return df, k_column, d_column

class StochasticStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy.
	"""

	def __init__(self, k_period: int = 14, d_period: int = 3):
		super().__init__("Stochastic", k_period, d_period)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on stochastic momentum.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = cross_over(df[k], df[d])
		sell = cross_under(df[k], df[d])

		return self.apply_signals(df, buy, sell)
	
class StochasticLevelStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy based on the overbought and oversold levels.
	"""

	def __init__(self, k_period: int = 14, d_period: int = 3, oversold: int = 20, overbought: int = 80):
		super().__init__("StochasticLevel", k_period, d_period)
		self.oversold = oversold
		self.overbought = overbought

		if not isinstance(self.overbought, int) or not isinstance(self.oversold, int):
			raise TypeError("oversold and overbought parameters must be integers")
		if self.oversold >= self.overbought:
			raise ValueError("the oversold level must be lower than the overbought level")
		if self.oversold <= 0 or self.overbought <= 0:
			raise ValueError("the oversold and overbought values must be positive integers")

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on stochastic momentum based on the overbought and oversold levels.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = cross_over_level(df[k], self.oversold)
		sell = cross_under_level(df[k], self.overbought)

		return self.apply_signals(df, buy, sell)
	
class StochasticFilteredStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy filtered by the %D line.
	"""

	def __init__(self, k_period: int = 14, d_period: int = 3):
		super().__init__("StochasticFiltered", k_period, d_period)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on stochastic momentum filtered by the %D line.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = (cross_over(df[k], df[d]) & (df[k] < 20) & (df[d] < 20))
		sell = (cross_under(df[k], df[d]) & (df[k] > 80) & (df[d] > 80))

		return self.apply_signals(df, buy, sell)
	
class StochasticCenterlineStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy based on the centerline.
	"""

	def __init__(self, k_period: int = 14, d_period: int = 3):
		super().__init__("StochasticCenterline", k_period, d_period)

	def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
		"""
		Generate trading signals based on stochastic momentum based on the centerline.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with trading signals.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = cross_over_level(df[k], 50)
		sell = cross_under_level(df[k], 50)

		return self.apply_signals(df, buy, sell)
