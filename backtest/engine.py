import pandas as pd

from backtest.portfolio import Portfolio
from models.results import BacktestResults
from models.event import MarketEvent

class BacktestEngine:
	def __init__(self, initial_cash: float = 10000, commission: float = 0.0):
		self.initial_cash = initial_cash
		self.commission = commission
		
	def _simulate(self, events):
		portfolio = Portfolio(
			self.initial_cash,
			self.commission
		)

		for event in events: 
			if event.signal == 1:
				portfolio.buy(event.date, event.price)

			elif event.signal == -1:
				portfolio.sell(event.date, event.price)

			portfolio.snapshot(event.date, event.price)

		portfolio.close(
			events[-1].date,
			events[-1].price
		)

		return portfolio

	def _build_events(self, signals):
		events = []

		for symbol, df in signals.items():
			for index, row in df.iterrows():
				events.append(
					MarketEvent(
						date = index,
						symbol = symbol,
						price = row["Close"],
						signal = row["Signal"]
					)
				)

		events.sort(key=lambda event: event.date)

		return events

	def run(self, strategy, data: dict[str, pd.DataFrame]):
		
		signals = {}
		for symbol, df in data.items():
			signals[symbol] = strategy.generate_signals(df)

		events = self._build_events(signals)
		
		portfolio = self._simulate(events)

		return BacktestResults.from_portfolio(portfolio)
