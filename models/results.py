from dataclasses import dataclass
from __future__ import annotations
from trade import Trade

@dataclass
class BacktestResults:
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
	winloss_ratio: float

	longest_holding: int
	shortest_holding: int
	average_holding: float

	cagr: float

	volatility: float

	sharpe_ratio: float

	sortino_ratio: float

	drawdown: float
	max_drawdown: float

	calmar_ratio: float

	gross_profit: float
	gross_loss: float
	profit_factor: float

	expectancy: float

	exposure: float

	recovery: float

	
