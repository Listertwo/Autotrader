import numpy as np
import pandas as pd

from indicators.basic import add_returns

class Risk:
	def __init__(self, annualize: bool = True, trading_periods: int = 252, lookback: int | None = None):
		if not isinstance(annualize, bool):
			raise TypeError("annualize must be a boolean")
		
		if not isinstance(trading_periods, int):
			raise TypeError("trading_periods must be an interger")
		if trading_periods <= 0:
			raise ValueError("trading_periods must be greater than zero")
		
		if lookback is not None:
			if not isinstance(lookback, int):
				raise TypeError("lookback must be an integer")
			if lookback <= 1:
				raise ValueError("lookback must be greater than one")
		
		self.annualize = annualize
		self.trading_periods = trading_periods
		self.lookback = lookback

		if lookback is not None:
			self.min_periods = lookback
		else:
			self.min_periods = 20

	def volatility(self, df: pd.DataFrame, date) -> float:



		col = "Returns_Close"

		if col not in df.columns:
			df = add_returns(df)

		returns = df.loc[df.index < date, col]
		
		if self.lookback is not None:
			returns = returns.tail(self.lookback)

		if len(returns) < self.min_periods:
			return None #Return static float for high risk investment, and still allow trade?
		
		vol = returns.std()

		if self.annualize:
			vol *= np.sqrt(self.trading_periods)

		return float(vol)
