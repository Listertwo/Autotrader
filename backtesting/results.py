from dataclasses import dataclass

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
	winning_trades: list
	
	losses: int
	largest_loss: float
	average_loss: float
	losing_trades: list

	win_rate: float
