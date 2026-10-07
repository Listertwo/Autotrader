import pandas as pd

from itertools import groupby

from backtest.portfolio import Portfolio
from models.results import BacktestResults
from models.event import MarketEvent
from utils.logger import logger

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
		
		if not isinstance(data, dict):
			raise TypeError("data must be a dictionary")
		else:
			for symbol in data:
				if not isinstance(symbol, str):
					raise TypeError(f"symbol {symbol} must be a string")
				if not isinstance(data[symbol], pd.DataFrame):
					raise TypeError(f"The data for data[{symbol}] must be a pandas DataFrame")
		
		logger.info("Starting backtest | strategy=%s | symbols=%s | initial_cash=$%.2f | commission=$%.2f", getattr(strategy, "name", type(strategy).__name__), ", ".join(data), self.initial_cash, self.commission)

		signals = {}
		for symbol, df in data.items():
			signals[symbol] = strategy.generate_signals(df)
			logger.info("Signals for %s: %d buy, %d sell (%d bars)", symbol, (signals[symbol]["Signal"] == 1).sum(), (signals[symbol]["Signal"] == -1).sum(), len(signals[symbol]))

		events = self._build_events(signals)
		
		portfolio = self._simulate(events)

		logger.info("Backtest finished | %d events | %s to %s | %d trade(s) | final cash=$%.2f", len(events), events[0].date if events else "n/a", events[-1].date if events else "n/a", len(portfolio.trades), portfolio.cash)

		return BacktestResults.from_portfolio(portfolio)
