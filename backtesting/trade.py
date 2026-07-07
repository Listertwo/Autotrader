from dataclasses import dataclass
from pandas import Timestamp

@dataclass
class Trade:
	entry_date: Timestamp
	exit_date: Timestamp

	entry_price: float
	exit_price: float

	shares: float

	commission: float

	profit: float
	return_pct: float
