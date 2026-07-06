import pandas as pd

from base import Strategy
from indicators.basic import add_rsi
from utils import cross_over_level, cross_under_level

class RsiStrategy(Strategy):
	"""
	A relative stregnth index momentum strategy.
	"""

	def __init__(self, period=14, oversold=30, overbought=70):
		super().__init__("RSI_Strategy")
		self.period = period
		self.oversold = oversold
		self.overbought = overbought

		if not isinstance(self.period, int) or not isinstance(self.oversold, int) or not isinstance(self.overbought, int):
			raise TypeError("period, oversold, and overbought must all be intergers")
		if self.oversold >= self.overbought:
			raise ValueError("the oversold level must be lower than the overbought level")
		if self.oversold <= 0 or self.overbought <= 0:
			raise ValueError("the oversold and overbought levels must both be positive intergers")

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

		if f"RSI_{self.period}_Close" not in df.columns:
			df = add_rsi(df, self.period)
		
		buy = cross_over_level(df[f"RSI_{self.period}_Close"], self.oversold):
		sell = cross_under_level(df[f"RSI_{self.period}_Close]", self.overbought):

		df["Signal"] = 0
		df.loc[buy, "Signal"] = 1
		df.loc[sell, "Signal"] = -1

		return df

class RsiCenterlineStrategy(Strategy):
	"""
	A relative stregnth index momentum strategy based on the centerline.
	"""
	def __init__(self, period: int = 14):
		super().__init__("RSI_Centerline")
		self.period = period
		self.oversold = 50
		self.overbought = 50

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

		if f"RSI_{self.period}_Close" not in df.columns:
			df = add_rsi(df, self.period)
		
		buy = cross_over_level(df[f"RSI_{self.period}_Close"], self.oversold):
		sell = cross_under_level(df[f"RSI_{self.period}_Close]", self.overbought):

		df["Signal"] = 0
		df.loc[buy, "Signal"] = 1
		df.loc[sell, "Signal"] = -1

		return df
