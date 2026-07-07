from dataclass import dataclass

@dataclass
class ProtfolioSnapshot:
	date: object

	cash: float
	
	shares: float
	
	market_value: float
	
	equity: float

class Portfolio:
	def __init__(self):
		self.history = []

	def add_snapshot():

	def equity_curve():

	def returns():

	def drawdowns():

	def max_drawdown():
