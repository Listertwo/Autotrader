from dataclasses import dataclass

from models.trade import Trade
from models.results import BacktestResults


@dataclass
class PortfolioSnapshot:
    date: object
    cash: float
    shares: float
    market_value: float
    equity: float


class Portfolio:
	def __init__(self, initial_cash: float, commission: float = 0.0):
		self.initial_cash = initial_cash
		self.cash = initial_cash
		self.commission = commission

		self.shares = 0.0

		self.entry_price = None
		self.entry_date = None

		self.trades: list[Trade] = []
		self.history: list[PortfolioSnapshot] = []

	@property
	def has_position(self):
		return self.shares > 0

	def buy(self, date, price) -> None:
		if price <= 0:
			raise ValueError("price must me postive.")
		if self.has_position:
			return

		cash_after_fee = self.cash - self.commission

		self.shares = cash_after_fee / price
		self.cash = 0.0

		self.entry_date = date
		self.entry_price = price

	def sell(self, date, price) -> None:
		if price <= 0:
			raise ValueError("price must me postive.")
		if not self.has_position:
			return

		cash = self.shares * price - self.commission

		cost_basis = self.shares * self.entry_price

		profit = cash - cost_basis

		return_pct = (profit / cost_basis) * 100

		holding_period = (date - self.entry_date).days

		self.trades.append(
			Trade(
				entry_date=self.entry_date,
				exit_date=date,
				entry_price=self.entry_price,
				exit_price=price,
				shares=self.shares,
				commission=self.commission,
				profit=profit,
				return_pct=return_pct,
				holding_period=holding_period,
			)
		)

		self.cash = cash
		self.shares = 0.0

		self.entry_date = None
		self.entry_price = None

	def close(self, date, price):

		if self.has_position:
			self.sell(date, price)

	def snapshot(self, date, price):

		market_value = self.shares * price

		self.history.append(
			PortfolioSnapshot(
				date=date,
				cash=self.cash,
				shares=self.shares,
				market_value=market_value,
				equity=self.cash + market_value,
			)
		)

	def equity_curve(self):
		return [s.equity for s in self.history]

	def returns(self):
		eq = self.equity_curve()

		if len(eq) < 2:
			return []

		return [
		(eq[i] / eq[i - 1]) - 1
		for i in range(1, len(eq))
		]

	def drawdowns(self):

		peak = float("-inf")
		drawdowns = []

		for equity in self.equity_curve():

			peak = max(peak, equity)

			drawdowns.append((equity - peak) / peak)

		return drawdowns

	def max_drawdown(self):

		dd = self.drawdowns()

		return min(dd) if dd else 0.0
