import pandas as pd

@dataclass
class MarketEvent:
	date: pd.Timestamp
	symbol: str
	price: float
	signal: int
