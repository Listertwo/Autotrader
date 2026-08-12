import pandas as pd

from dataclasses import dataclass

from models.trade import Trade

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

	def buy(self, symbol, date, price) -> None:
		if price <= 0:
			raise ValueError("price must me postive.")
		if self.positions[symbol].get("shares", 0) > 0:
			return

		cash_after_fee = self.cash - self.commission

		if cash_after_fee <= 0:
			raise ValueError("Not enough cash to execute trade.")
		
		shares = cash_after_fee / price
		self.cash = 0.0

		self.entry_date = date
		self.entry_price = price

		self.positions[symbol].update({"entry_date": date, "entry_price": price, "shares": shares})

	def sell(self, symbol, date, price) -> None:
		if price <= 0:
			raise ValueError("price must me postive.")
		if not self.positions[symbol].get("shares", 0) > 0:
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

		self.positions[symbol].update({"entry_date": None, "entry_price": None, "shares": 0})

	def close(self, date, prices: dict[str, float]) -> None:
		for symbol, position in self.positions.items():
			if position.get("shares", 0) > 0:
				price = prices.get(symbol)

				if price is None:
					raise ValueError(f"Price for symbol {symbol} not provided in prices dictionary.")

				self.sell(symbol, date, price)

	def snapshot(self, date, prices: dict[str, float]) -> None:
		if price <= 0:
			raise ValueError("price must be positive")

		market_value: float = 0.0

		for symbol, price in prices.items():
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
