from dataclasses import dataclass
from pandas import Timestamp

@dataclass
class Trade:
	def __str__(self) -> str:
		return(
			f"{self.entry_date.date()} -> {self.exit_date.date()} | "
        	f"${self.entry_price:.2f} -> ${self.exit_price:.2f} | "
        	f"Profit ${self.profit:.2f} ({self.return_pct:.2f}%)"
		)
	
	entry_date: Timestamp
	exit_date: Timestamp

	entry_price: float
	exit_price: float

	shares: float

	commission: float

	profit: float
	return_pct: float

	holding_period: int
