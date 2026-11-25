import pandas as pd

from strategies.base import Strategy
from indicators.basic import add_rsi, add_macd, add_stochastic
from strategies.utils import cross_under, cross_over, cross_under_level, cross_over_level

class BaseRsiStrategy(Strategy):
	"""
	A relative strength index momentum strategy.
	"""

	default_params = {"period": 14}
	
	def validate(self):
		period = self.params["period"]
		if not isinstance(period, int) or period <= 0:
			raise TypeError("period must be a positive integer")

	def _prepare_rsi(self, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
		"""
		Prepare the DataFrame by adding the RSI column if it doesn't exist.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		pd.DataFrame
			DataFrame with the RSI column added.
		"""
		
		column_name = f"RSI_{self.params['period']}_Close"
		
		if column_name not in df.columns:
			df = add_rsi(df, self.params["period"])
		
		return df, column_name

class RsiStrategy(BaseRsiStrategy):
	"""
	A relative stregnth index momentum strategy.
	"""

	default_params = {**BaseRsiStrategy.default_params, "oversold": 30, "overbought": 70}
	
	def validate(self):
		super().validate()
		oversold, overbought = self.params["oversold"], self.params["overbought"]
		if not isinstance(oversold, int) or not isinstance(overbought, int):
			raise TypeError("oversold, and overbought must both be integers")
		if not oversold <= overbought:
			raise ValueError("the oversold level must be lower than the overbought level")
		if not overbought < 100:
			raise ValueError("overbought value must be less than 100")
		if not 0 < oversold:
			raise ValueError("oversold must be a positive integer greater than 0")
	
	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
        Generate trading signals based on strength index momentum.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        tuple[pd.DataFrame, pd.Series, pd.Series]
            The DataFrame, the buy mask, and the sell mask.
        """

		df, column_name = self._prepare_rsi(df)

		buy = cross_over_level(df[column_name], self.params["oversold"])
		sell = cross_under_level(df[column_name], self.params["overbought"])

		return df, buy, sell

class RsiCenterlineStrategy(BaseRsiStrategy):
	"""
	A relative stregnth index momentum strategy based on the centerline.
	"""
	
	default_params = {**BaseRsiStrategy.default_params, "buy_above": 50, "sell_below": 50}

	def validate(self):
		super().validate()
		buy, sell = self.params["buy_above"], self.params["sell_below"]
		if not isinstance(buy, int) or not isinstance(sell, int):
			raise TypeError("buy_above and sell_below must be integers")
		if not sell <= buy:
			raise ValueError("sell_below must be less than buy_above")
		if not sell <= 50 or not 0 <= sell:
			raise ValueError("sell_below must be less than the centerline and greater than 0")
		if not 50 <= buy or not buy <= 100:
			raise ValueError("buy_above must be greater than the centerline and less than 100")
	
	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
        Generate trading signals based on strength index momentum based on the centerline.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        tuple[pd.DataFrame, pd.Series, pd.Series]
            The DataFrame, the buy mask, and the sell mask.
        """

		df, column_name = self._prepare_rsi(df)
		
		buy = cross_over_level(df[column_name], self.params["buy_above"])
		sell = cross_under_level(df[column_name], self.params["sell_below"])

		return df, buy, sell

class BaseMacdStrategy(Strategy):
	default_params = {"fast": 12, "slow": 26, "signal": 9}

	def validate(self):
		fast, slow, signal = self.params["fast"], self.params["slow"], self.params["signal"]
		if not isinstance(fast, int) or not isinstance(slow, int) or not isinstance(signal, int):
			raise TypeError("fast, slow, and signal must all be positive integers")
		if fast <= 0 or slow <= 0 or signal <= 0:
			raise ValueError("fast, slow, and signal must all be positive integers")
		if fast >= slow:
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

		fast, slow, signal = self.params["fast"], self.params["slow"], self.params["signal"]
		
		macd_column = f"MACD_f{fast}_s{slow}_g{signal}_Close"
		signal_column = f"MACD_Signal_f{fast}_s{slow}_g{signal}_Close"
		histogram_column = f"MACD_Histogram_f{fast}_s{slow}_g{signal}_Close"
		
		if macd_column not in df.columns or signal_column not in df.columns or histogram_column not in df.columns:
			df = add_macd(df, fast, slow, signal)
		return df, macd_column, signal_column, histogram_column

class MacdStrategy(BaseMacdStrategy):
	"""
	A moving average convergence divergence momentum strategy.
	"""

	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on moving average convergence divergence momentum.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""

		df, macd, signal, hist = self._prepare_macd(df)

		buy = cross_over(df[macd], df[signal])
		sell = cross_under(df[macd], df[signal])

		return df, buy, sell
	
class MacdZeroLineStrategy(BaseMacdStrategy):
	"""
	A moving average convergence divergence momentum strategy based on the zero line.
	"""

	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on moving average convergence divergence momentum based on the zero line.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""

		df, macd, signal, hist = self._prepare_macd(df)

		buy = cross_over_level(df[macd], 0)
		sell = cross_under_level(df[macd], 0)

		return df, buy, sell
	
class MacdHistogramStrategy(BaseMacdStrategy):
	"""
	A moving average convergence divergence momentum strategy based on the histogram.
	"""

	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on moving average convergence divergence momentum based on the histogram.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""

		df, macd, signal, hist = self._prepare_macd(df)
		
		buy = cross_over_level(df[hist], 0)
		sell = cross_under_level(df[hist], 0)

		return df, buy, sell

class BaseStochasticStrategy(Strategy):
	"""
	A base class for stochastic momentum strategies.
	"""

	default_params = {"k_period": 14, "d_period": 3}
	
	def validate(self):
		k_period, d_period = self.params["k_period"], self.params["d_period"]
		if not isinstance(k_period, int) or not isinstance(d_period, int):
			raise TypeError("k_period and d_period must both be positive integers")
		if k_period <= 0 or d_period <= 0:
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

		k_period, d_period = self.params["k_period"], self.params["d_period"]
		
		k_column = f"Stochastic_%K_{k_period}_{d_period}"
		d_column = f"Stochastic_%D_{k_period}_{d_period}"
		
		if k_column not in df.columns or d_column not in df.columns:
			df = add_stochastic(df, k_period, d_period)
		return df, k_column, d_column

class StochasticStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy.
	"""
	
	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on stochastic momentum.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = cross_over(df[k], df[d])
		sell = cross_under(df[k], df[d])

		return df, buy, sell
	
class StochasticLevelStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy based on the overbought and oversold levels.
	"""

	default_params = {**BaseStochasticStrategy.default_params, "oversold": 20, "overbought": 80}
	
	def validate(self):
		super().validate()
		oversold, overbought = self.params["oversold"], self.params["overbought"]
		if not isinstance(overbought, int) or not isinstance(oversold, int):
			raise TypeError("oversold and overbought parameters must be integers")
		if oversold >= overbought:
			raise ValueError("the oversold level must be lower than the overbought level")
		if oversold <= 0 or overbought <= 0:
			raise ValueError("the oversold and overbought values must be positive integers")

	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on stochastic momentum based on the overbought and oversold levels.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""
		
		oversold, overbought = self.params["oversold"], self.params["overbought"]
		df, k, d = self._prepare_stochastic(df)

		buy = cross_over_level(df[k], oversold)
		sell = cross_under_level(df[k], overbought)

		return df, buy, sell
	
class StochasticFilteredStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy filtered by the %D line.
	"""

	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on stochastic momentum filtered by the %D line.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = (cross_over(df[k], df[d]) & (df[k] < 20) & (df[d] < 20))
		sell = (cross_under(df[k], df[d]) & (df[k] > 80) & (df[d] > 80))

		return df, buy, sell
	
class StochasticCenterlineStrategy(BaseStochasticStrategy):
	"""
	A stochastic momentum strategy based on the centerline.
	"""
	default_params = {**BaseStochasticStrategy.default_params, "buy_above": 50, "sell_below": 50}

	def validate(self):
		super().validate()
		buy, sell = self.params["buy_above"], self.params["sell_below"]
		if not isinstance(buy, int) or not isinstance(sell, int):
			raise TypeError("buy_above and sell_below must be integers")
		if not sell <= buy:
			raise ValueError("sell_below must be less than buy_above")
		if not sell <= 50 or not 0 <= sell:
			raise ValueError("sell_below must be less than the centerline and greater than 0")
		if not 50 <= buy or not buy <= 100:
			raise ValueError("buy_above must be greater than the centerline and less than 100")

	def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
		"""
		Generate trading signals based on stochastic momentum based on the centerline.

		Parameters
		----------
		df : pd.DataFrame
			Historical market data.

		Returns
		-------
		tuple[pd.DataFrame, pd.Series, pd.Series]
			The DataFrame, the buy mask, and the sell mask.
		"""

		df, k, d = self._prepare_stochastic(df)

		buy = cross_over_level(df[k], self.params["buy_above"])
		sell = cross_under_level(df[k], self.params["sell_below"])

		return df, buy, sell
