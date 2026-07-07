from dataclasses import dataclass

@dataclass
class BacktestResults:
	initial_cash: float
	final_cash: float

	total_return: float

	trades: int

	wins: int
	losses: int

	win_rate: float
