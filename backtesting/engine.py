import pandas as pd

from typing import tuple
from portfolio import Portfolio
from strategies.base import Strategy
from models.trade import Trade
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

			if signal == 1:
				portfolio.buy(index, price)

			elif signal == -1:
				portfolio.sell(index, price)

			portfolio.snapshot(index, price)

		portfolio.close(
			signals.index[-1],
			signals.iloc[-1]["Close"]
		)

		return portfolio
	
	def run(self, strategy, df):

		signals = strategy.generate_signals(df)

		portfolio = self._simulate(signals)

		return BacktestResults.from_portfolio(portfolio)
