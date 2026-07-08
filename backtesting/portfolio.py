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

	def buy(self, date, price):

		if self.has_position:
			return

		cash_after_fee = self.cash - self.commission

		self.shares = cash_after_fee / price
		self.cash = 0.0

		self.entry_date = date
		self.entry_price = price

	def sell(self, date, price):

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
	
	def from_portfolio(self, portfolio: Portfolio, initial_cash: float) -> BacktestResults:
		trades = portfolio.trades
		cash = initial_cash

		trade_amount = len(trades)
		
		total_return = sum(trade.profit for trade in trades)
		average_return = (total_return / trade_amount if trade_amount else 0.0)
		
		wins = sum(trade.profit > 0 for trade in trades)
		losses = sum(trade.profit < 0 for trade in trades)

		largest_win = max((trade.profit for trade in trades), default=0.0)
		largest_loss = min((trade.profit for trade in trades), default=0.0)

		winning_trades = [
			trade
			for trade in trades
			if trade.profit >= 0
		]
		average_win = (sum(winning_trades) / len(winning_trades) if winning_trades else 0.0)

		losing_trades = [
			trade
			for trade in trades
			if trade.profit < 0
		]
		average_loss = (sum(losing_trades) / len(losing_trades) if losing_trades else 0.0)

		win_rate = (wins / trade_amount if trade_amount else 0.0)

		longest_holding = max((trade.holding_period for trade in trades), default=0.0)
		shortest_holding = min((trade.holding_period for trade in trades), default=0.0)
		average_holding = (sum((trade.holding_period for trade in trades), default=0.0) / trade_amount if trade_amount else 0.0)
		
		return BacktestResults.from_portfolio(
			initial_cash = self.initial_cash,
			final_cash = cash,
			total_return = total_return,
			average_return = average_return,
			trades = trade_amount,
			wins = wins,
			largest_win = largest_win,
			average_win = average_win,
			winning_trades = winning_trades,
			losses = losses,
			largest_loss = largest_loss,
			average_loss = average_loss,
			losing_trades = losing_trades,
			win_rate = win_rate,
			longest_holding = longest_holding,
			shortest_holding = shortest_holding,
			average_holding = average_holding
		)
    