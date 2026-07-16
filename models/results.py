from __future__ import annotations

import pandas as pd

from dataclasses import dataclass

from models.trade import Trade
from backtest.portfolio import Portfolio

@dataclass
class BacktestResults:
	@classmethod
	def from_portfolio(cls, portfolio: Portfolio) -> BacktestResults:
		trades = portfolio.trades
		cash = portfolio.cash
		returns = pd.Series(portfolio.returns())
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
		average_win = (sum(trade.profit for trade in winning_trades) / len(winning_trades) if winning_trades else 0.0)

		losing_trades = [
			trade
			for trade in trades
			if trade.profit < 0
		]
		average_loss = (sum(trade.profit for trade in losing_trades) / len(losing_trades) if losing_trades else 0.0)

		win_rate = (wins / trade_amount if trade_amount else 0.0)
		loss_rate = (losses / trade_amount if trade_amount else 0.0)

		winloss_ratio = (average_win / abs(average_loss) if average_loss else 0.0)

		longest_holding = max((trade.holding_period for trade in trades), default=0.0)
		shortest_holding = min((trade.holding_period for trade in trades), default=0.0)
		average_holding = (sum(trade.holding_period for trade in trades) / trade_amount if trade_amount else 0.0)

		sharpe_ratio, sharpe_rating = cls.calculate_sharpe(returns)
		
		gross_profit, gross_loss, profit_factor, profit_rating = cls.calculate_profit(trades)

		expectancy = (win_rate * average_win) + (loss_rate * average_loss)
		
		return cls(
			initial_cash = portfolio.initial_cash,
			final_cash = cash,
			total_return = total_return,
			average_return = average_return,
			trades = trades,
			trade_count = trade_amount,
			wins = wins,
			largest_win = largest_win,
			average_win = average_win,
			winning_trades = winning_trades,
			losses = losses,
			largest_loss = largest_loss,
			average_loss = average_loss,
			losing_trades = losing_trades,
			win_rate = win_rate,
			winloss_ratio = winloss_ratio,
			longest_holding = longest_holding,
			shortest_holding = shortest_holding,
			average_holding = average_holding,
			cagr = cls.calculate_cagr(portfolio),
			volatility = cls.calculate_volatility(returns),
			sharpe_ratio = sharpe_ratio,
			sharpe_rating = sharpe_rating,
			sortino_ratio = cls.calculate_sortino(returns),
			drawdown = portfolio.drawdowns(),
			max_drawdown = portfolio.max_drawdown(),
			calmar_ratio = cls.calculate_calmar(portfolio),
			gross_profit = gross_profit,
			gross_loss = gross_loss,
			profit_factor = profit_factor,
			profit_rating = profit_rating,
			expectancy = expectancy,
			exposure = cls.calculate_exposure(trades),
			recovery = cls.calculate_recovery(portfolio, trades)
		)

	@staticmethod
	def calculate_cagr(portfolio: Portfolio) -> float:
		first_date = portfolio.history[0].date
		last_date = portfolio.history[-1].date
		years = (last_date - first_date).days / 365.25

		if years <= 0:
			return 0.0
		
		return (portfolio.cash / portfolio.initial_cash) ** (1/years) - 1

	@staticmethod
	def calculate_volatility(returns: pd.Series) -> float:
		return returns.std() * (252 ** 0.5)

	@staticmethod
	def calculate_sharpe(returns: pd.Series) -> tuple[float, str]:
		sqrt252 = 252 ** 0.5
		
		ratio = sqrt252 * returns.mean() / (returns.std())

		if ratio < 1:
			rating = "Mediocre"
		elif ratio < 2:
			rating = "Good"
		elif ratio < 3:
			rating = "Excellent"
		else:
			rating = "Exceptional"
		
		return ratio, rating

	@staticmethod
	def calculate_sortino(returns: pd.Series) -> float:
		sqrt252 = 252 ** 0.5
		downside = returns[returns < 0]

		return sqrt252 * (returns.mean() / downside.std())

	@staticmethod
	def calculate_calmar(portfolio: Portfolio) -> float:
		cagr = BacktestResults.calculate_cagr(portfolio)

		return cagr / abs(portfolio.max_drawdown())

	@staticmethod
	def calculate_profit(trades: list[Trade]) -> tuple[float, float, float, str]:
		gross_profit = sum(
			trade.profit
			for trade in trades
			if trade.profit > 0
		)

		gross_loss = abs(sum(
			trade.profit
			for trade in trades
			if trade.profit < 0
		))

		profit_factor = gross_profit / gross_loss if gross_loss else float("inf")

		if profit_factor >= 2:
			profit_rating = "Excellent"
		elif profit_factor >= 1:
			profit_rating = "Net Positive"
		else:
			profit_rating = "Losing"

		return gross_profit, gross_loss, profit_factor, profit_rating

	@staticmethod
	def calculate_exposure(trades: list[Trade]) -> float:
		days_in_market = sum(
			trade.holding_period
			for trade in trades
		)

		return days_in_market / 365 #Later implement total market day tally, possibly stored in Portfolio?

	@staticmethod
	def calculate_recovery(portfolio: Portfolio, trades: list[Trade]) -> float:
		net_profit = sum(
			trade.profit
			for trade in trades
		)

		return net_profit / portfolio.max_drawdown()

	def __str__(self) -> str:
		return (
			f"\n"
			f"{'=' * 60}\n"
			f"BACKTEST RESULTS\n"
			f"{'=' * 60}\n"
			f"Initial Cash:      ${self.initial_cash:,.2f}\n"
			f"Final Cash:        ${self.final_cash:,.2f}\n"
			f"Net Profit:        ${self.total_return:,.2f}\n"
			f"Average Trade:     ${self.average_return:,.2f}\n"
			f"\n"
			f"Trades:            {self.trade_count}\n"
			f"Wins:              {self.wins}\n"
			f"Losses:            {self.losses}\n"
			f"Win Rate:          {self.win_rate:.2%}\n"
			f"\n"
			f"Largest Win:       ${self.largest_win:,.2f}\n"
			f"Largest Loss:      ${self.largest_loss:,.2f}\n"
			f"Average Win:       ${self.average_win:,.2f}\n"
			f"Average Loss:      ${self.average_loss:,.2f}\n"
			f"\n"
			f"Profit Factor:     {self.profit_factor:.2f}, {self.profit_rating}\n"
			f"Sharpe Ratio:      {self.sharpe_ratio:.2f}, {self.sharpe_rating}\n"
			f"Sortino Ratio:     {self.sortino_ratio:.2f}\n"
			f"Calmar Ratio:      {self.calmar_ratio:.2f}\n"
			f"\n"
			f"CAGR:              {self.cagr:.2%}\n"
			f"Volatility:        {self.volatility:.2%}\n"
			f"Max Drawdown:      {self.max_drawdown:.2%}\n"
			f"Exposure:          {self.exposure:.2%}\n"
			f"Recovery Factor:   {self.recovery:.2f}\n"
			f"{'=' * 60}"
		)

	def print_trades(self):
		print("\nTrades")
		print("=" * 60)

		for trade in self.trades:
			print(trade)
	
	initial_cash: float
	final_cash: float

	total_return: float
	average_return: float

	trades: list[Trade]
	trade_count: int

	wins: int
	largest_win: float
	average_win: float
	winning_trades: list[Trade]
	
	losses: int
	largest_loss: float
	average_loss: float
	losing_trades: list[Trade]

	win_rate: float
	winloss_ratio: float

	longest_holding: int
	shortest_holding: int
	average_holding: float

	cagr: float

	volatility: float

	sharpe_ratio: float
	sharpe_rating: str

	sortino_ratio: float

	drawdown: float
	max_drawdown: float

	calmar_ratio: float

	gross_profit: float
	gross_loss: float
	profit_factor: float
	profit_rating: str

	expectancy: float

	exposure: float

	recovery: float
