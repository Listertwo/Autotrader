from strategies.crossover import SmaCrossoverStrategy

class GoldenCrossStrategy(SmaCrossoverStrategy):
	"""
    A preset strategy that is based off of the SMA strategy.

	A 1 indicates a Golden Cross -> Bullish Market.
	A -1 indicates a Death Cross -> Bearish Market.
    """
	
	default_params = {"fast": 50, "slow": 200}
	
	def validate(self):
	    super().validate()
	    if self.params != self.default_params:
	        raise ValueError("GoldenCrossStrategy is fixed at 50/200; use SmaCrossoverStrategy for other windows")
