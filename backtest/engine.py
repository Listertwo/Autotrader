import pandas as pd

from itertools import groupby

from backtest.portfolio import Portfolio
from risk.allocation import Allocator
from risk.riskclass import Risk
from models.results import BacktestResults
from models.event import MarketEvent
from utils.logger import logger

class BacktestEngine:
	def __init__(self, initial_cash: float = 10000, commission: float = 0.0, slippage_bps: float = 0.0, target_risk: float = 0.02, min_allocation: float = 0.0, max_allocation: float = 0.25, max_volatility: float = 0.50, annualize: bool = True, trading_periods: int = 252, lookback: int | None = None):
		self.initial_cash = initial_cash
		self.commission = commission
		self.slippage_bps = slippage_bps

		self.allocator = Allocator(target_risk=target_risk, min_allocation=min_allocation, max_allocation=max_allocation, max_volatility=max_volatility)
		self.risk = Risk(annualize=annualize, trading_periods=trading_periods, lookback=lookback)
		
	def _simulate(self, events, data, label):
		portfolio = Portfolio(
			self.initial_cash,
			self.commission
		)

		last_prices = {}
		last_date = None

		for date, date_events in groupby(events, key=lambda event: event.date):
			date_events = list(date_events)

			#Sell Loop
			for event in date_events: 
				if event.signal == -1:
					portfolio.sell(event.symbol, event.date, self._fill_price(event.open, "sell"))
				last_prices[event.symbol] = event.close

			#Buy Loop
			for event in date_events:
				if event.signal == 1:
					volatility = self.risk.volatility(data[event.symbol], event.date)
					allocation = self.allocator.calculate(volatility)
					portfolio.buy(event.symbol, event.date, self._fill_price(event.open, "buy"), allocation, label)
				last_prices[event.symbol] = event.close
			
			portfolio.snapshot(date, last_prices)
			last_date = date

		if last_date is not None:
			portfolio.close(
				last_date,
				last_prices
			)

		return portfolio

	def _build_events(self, signals):
		events = []

		for symbol, df in signals.items():
			pending = df["Signal"].shift(1, fill_value=0)
			
			if df["Signal"].iloc[-1] != 0:
				logger.info("Dropping %s signal on the last bar (%s): no next open to fill at", symbol, df.index[-1])
			
			for index, row in df.iterrows():
				events.append(
					MarketEvent(
						date = index,
						symbol = symbol,
						close = row["Close"],
						open = row["Open"],
						signal = int(pending.loc[index])
					)
				)

		events.sort(key=lambda event: event.date)

		return events

	def _fill_price(self, open: float, side: str) -> float:
		slip = self.slippage_bps / 10000
		if side == "buy":
			return open * (1 + slip)
		return open * (1 - slip)

	def run(self, strategy, data: dict[str, pd.DataFrame]):
		
		if not isinstance(data, dict):
			raise TypeError("data must be a dictionary")
		else:
			for symbol in data:
				if not isinstance(symbol, str):
					raise TypeError(f"symbol {symbol} must be a string")
				if not isinstance(data[symbol], pd.DataFrame):
					raise TypeError(f"The data for data[{symbol}] must be a pandas DataFrame")
		
		logger.info("Starting backtest | strategy=%s | symbols=%s | initial_cash=$%.2f | commission=$%.2f", strategy.label, ", ".join(data), self.initial_cash, self.commission)

		signals = {}
		for symbol, df in data.items():
			df, buy, sell = strategy.generate_signals(df)
			signals[symbol] = strategy.apply_signals(df, buy, sell)
			logger.info("Signals for %s: %d buy, %d sell (%d bars)", symbol, (signals[symbol]["Signal"] == 1).sum(), (signals[symbol]["Signal"] == -1).sum(), len(signals[symbol]))

		events = self._build_events(signals)
		
		portfolio = self._simulate(events, data, strategy.label)

		logger.info("Backtest finished | %d events | %s to %s | %d trade(s) | final cash=$%.2f", len(events), events[0].date if events else "n/a", events[-1].date if events else "n/a", len(portfolio.trades), portfolio.cash)

		return BacktestResults.from_portfolio(portfolio)
