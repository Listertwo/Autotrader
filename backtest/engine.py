import pandas as pd

from itertools import groupby

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

		last_prices = {}

		for date, date_events in groupby(events, key=lambda event: event.date):
			date_events = list(date_events)

			for event in date_events: 
				last_prices[event.symbol] = event.price
				last_date = event.date

				if event.signal == 1:
					portfolio.buy(event.symbol, event.date, event.price)

				elif event.signal == -1:
					portfolio.sell(event.symbol, event.date, event.price)

			portfolio.snapshot(date, last_prices)


		portfolio.close(
			last_date,
			last_prices
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
