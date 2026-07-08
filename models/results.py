from dataclasses import dataclass
from __future__ import annotations
from trade import Trade

@dataclass
class BacktestResults:
	@classmethod
	def from_portfolio(cls, portfolio: Portfolio) -> BacktestResults:
		trades = portfolio.trades
		cash = portfolio.cash

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

		longest_holding = max((trade.holding_period for trade in trades), default=0.0)
		shortest_holding = min((trade.holding_period for trade in trades), default=0.0)
		average_holding = (sum(trade.holding_period for trade in trades) / trade_amount if trade_amount else 0.0)
		
		return cls(
			initial_cash = portfolio.initial_cash,
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
	
	initial_cash: float
	final_cash: float

	total_return: float
	average_return: float

	trades: int

	wins: int
	largest_win: float
	average_win: float
	winning_trades: list[Trade]
	
	losses: int
	largest_loss: float
	average_loss: float
	losing_trades: list[Trade]

	win_rate: float

	longest_holding: int
	shortest_holding: int
	average_holding: float
