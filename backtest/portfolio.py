import pandas as pd

from dataclasses import dataclass

from models.trade import Trade
from utils.logger import logger

@dataclass
class PortfolioSnapshot:
    date: pd.Timestamp
    cash: float
    positions: dict[str, dict[str, float]]
    market_value: float
    equity: float


class Portfolio:
	def __init__(self, initial_cash: float, commission: float = 0.0):
		self.initial_cash = initial_cash
		self.cash = initial_cash
		self.commission = commission

		self.positions: dict[str, dict[str, float]] = {}

		self.trades: list[Trade] = []
		self.history: list[PortfolioSnapshot] = []

	#@property
	#def has_position(self) -> bool:
		#return self.shares > 0

	@property
	def equity(self) -> float:
		if self.has_position:
			raise RuntimeError("Equity depends on current market price. Use snapshot() during a simulation.")
		
		return self.cash

	def buy(self, symbol, date, price, allocation) -> None:
		if symbol not in self.positions:
			self.positions[symbol] = {"entry_date": None, "entry_price": None, "shares": 0}
		if price <= 0:
			raise ValueError("price must me postive.")
		if self.positions[symbol].get("shares", 0) > 0:
			logger.debug("Ignoring BUY signal for %s on %s: position already open", symbol, date)
			return

		if self.history:
			current_equity = self.history[-1].equity
		else:
			current_equity = self.cash

		cash_after_fee = self.cash - self.commission

		if cash_after_fee <= 0:
			raise ValueError("Not enough cash to execute trade.")
		
		target_value = current_equity * allocation
		actual_value = min(target_value, cash_after_fee)
		
		shares = actual_value / price
		self.cash = cash_after_fee - actual_value

		self.positions[symbol].update({"entry_date": date, "entry_price": price, "shares": shares})

		if shares > 0:
			logger.info("BUY  %s | %s | price=$%.2f | shares=%.4f | value=$%.2f | allocation=%.2f%% | cash left=$%.2f", symbol, date, price, shares, actual_value, allocation * 100, self.cash)
		else:
			logger.debug("No shares bought for %s on %s: allocation was %.4f", symbol, date, allocation)

	def sell(self, symbol, date, price) -> None:
		if price <= 0:
			raise ValueError("price must me postive.")
		if not self.positions[symbol].get("shares", 0) > 0:
			logger.debug("Ignoring SELL signal for %s on %s: no open position", symbol, date)
			return
		if symbol not in self.positions:
			logger.debug("Ignoring SELL signal for %s on %s: symbol not tracked", symbol, date)
			return

		shares = self.positions[symbol].get("shares", 0)
		entry_price = self.positions[symbol].get("entry_price", 0)
		entry_date = self.positions[symbol].get("entry_date", None)

		self.cash = shares * price - self.commission

		cost_basis = shares * entry_price

		profit = self.cash - cost_basis

		return_pct = (profit / cost_basis) * 100
		
		holding_period = (date - entry_date).days

		self.trades.append(
			Trade(
				entry_date=entry_date,
				exit_date=date,
				entry_price=entry_price,
				exit_price=price,
				shares=shares,
				commission=self.commission,
				profit=profit,
				return_pct=return_pct,
				holding_period=holding_period,
			)
		)

		logger.info("SELL %s | %s | price=$%.2f | shares=%.4f | profit=$%.2f (%.2f%%) | held %d day(s) | cash=$%.2f", symbol, date, price, shares, profit, return_pct, holding_period, self.cash)

		self.positions[symbol].update({"entry_date": None, "entry_price": None, "shares": 0})

	def close(self, date, prices: dict[str, float]) -> None:
		open_symbols = [symbol for symbol, position in self.positions.items() if position.get("shares", 0) > 0]

		if open_symbols:
			logger.info("Closing %d open position(s) at end of data (%s): %s", len(open_symbols), date, ", ".join(open_symbols))

		for symbol, position in self.positions.items():
			if position.get("shares", 0) > 0:
				price = prices.get(symbol)

				if price is None:
					raise ValueError(f"Price for symbol {symbol} not provided in prices dictionary.")

				self.sell(symbol, date, price)

	def snapshot(self, date, prices: dict[str, float]) -> None:
		market_value: float = 0.0

		for symbol, price in prices.items():
			if price <= 0:
				raise ValueError("price must be positive")
			if symbol not in self.positions:
				self.positions[symbol] = {"entry_date": None, "entry_price": None, "shares": 0}

			market_value += self.positions[symbol].get("shares", 0) * price

		self.history.append(
			PortfolioSnapshot(
				date=date,
				cash=self.cash,
				positions=self.positions,
				market_value=market_value,
				equity=self.cash + market_value,
			)
		)

	def equity_curve(self) -> list[float]:
		return [s.equity for s in self.history]

	def returns(self) -> list[float]:
		eq = self.equity_curve()

		if len(eq) < 2:
			return []

		return [
		(eq[i] / eq[i - 1]) - 1
		for i in range(1, len(eq))
		]

	def drawdowns(self) -> list[float]:
		peak = self.equity_curve()[0]
		equity = self.equity_curve()
		drawdowns = []

		if not equity:
			return []
		
		for equity in self.equity_curve():

			peak = max(peak, equity)

			drawdowns.append((equity - peak) / peak)

		return drawdowns

	def max_drawdown(self) -> float:

		dd = self.drawdowns()

		return min(dd) if dd else 0.0
