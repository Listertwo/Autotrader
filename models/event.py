from dataclasses import dataclass
import pandas as pd

@dataclass
class MarketEvent:
	date: pd.Timestamp
	symbol: str
	open: float
	close: float
	signal: int
