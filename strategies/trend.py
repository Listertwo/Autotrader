from base import Strategy
from crossover import SmaCrossoverStrategy

class GoldenCrossStrategy(SmaCrossoverStrategy):
	def __init__(self):
		super().__init__(50, 200)
