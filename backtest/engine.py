import pandas as pd

from backtest.portfolio import Portfolio
from models.results import BacktestResults

class BacktestEngine:
	def __init__(self, initial_cash: float = 10000, commission: float = 0.0):
		self.initial_cash = initial_cash
		self.commission = commission
		
	def _simulate(self, signals):
		portfolio = Portfolio(
			self.initial_cash,
			self.commission
		)

		for index, row in signals.iterrows():

			signal = row["Signal"]
			price = row["Close"]

			index = pd.to_datetime(index)

			if signal == 1:
				portfolio.buy(index, price)

			elif signal == -1:
				portfolio.sell(index, price)

			portfolio.snapshot(index, price)

		portfolio.close(
			pd.to_datetime(signals.index[-1]),
			signals.iloc[-1]["Close"]
		)

		return portfolio
	
	def run(self, strategy, df):

		df, buy, sell = strategy.generate_signals(df)

		signals = strategy.apply_signals(df, buy, sell)

		portfolio = self._simulate(signals)

		return BacktestResults.from_portfolio(portfolio)
