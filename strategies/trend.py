from base import Strategy
from crossover import SmaCrossoverStrategy

class GoldenCrossStrategy(SmaCrossoverStrategy):
	 """
    A preset strategy that is based off of the SMA strategy.

	A 1 indicates a Golden Cross -> Bullish Market.
	A -1 indicates a Death Cross -> Bearish Market.
    """
	
	def __init__(self):
		super().__init__(50, 200)
