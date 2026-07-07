import pandas as pd
from strategies.base import Strategy

class BacktestEngine:
	def __init__(self, initial_cash: float = 10000, commission: float = 0.0):
		self.initial_cash = initial_cash
		self.commission = commission
		
	def _simulate(self, signals: pd.DataFrame) -> float:
		cash = self.initial_cash
		shares = 0
		
		for index, row in signals.iterrows():
			row_signal = row["Signal"]
			row_price = row["Close"]

			if row_signal == 1 and shares == 0:
				shares = cash / row_price
				cash = 0

			if row_signal == -1 and not shares == 0:
				cash = shares * row_price
				shares = 0

		if shares > 0:
			cash = shares * signals.iloc[-1]["Close"]
			shares = 0

		return cash

	def _calculate_results(self, cash: float) -> dict[str, float]:
		return {
			"Initial Cash": self.initial_cash,
			"Final Cash": cash,
		}
	
	def run(self, strategy: Strategy, df: pd.DataFrame) -> dict[str, float]:
		signals = strategy.generate_signals(df)
		trades = self._simulate(signals)
		return self._calculate_results(trades)
