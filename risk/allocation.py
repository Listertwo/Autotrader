from utils.logger import logger


class Allocator:
	def __init__(self, target_risk: float = 0.02, min_allocation: float = 0.0, max_allocation: float = 0.25, max_volatility: float = 0.20):
		if not isinstance(target_risk, (int, float)):
			raise TypeError("target_risk must be a number")
		if target_risk <= 0:
			raise ValueError("target_risk must be positive")

		if not isinstance(min_allocation, float):
			raise TypeError("min_allocation must be a float")
		if min_allocation < 0:
			raise ValueError("min_allocation must be positive or zero")

		if not isinstance(max_allocation, float):
			raise TypeError("max_allocation must be a float")
		if max_allocation <= 0:
			raise ValueError("max_allocation must be positive")
		if max_allocation < min_allocation:
			raise ValueError("max_allocation must be greater than min_allocation")

		if not isinstance(max_volatility, float):
			raise TypeError("max_volatility must be a float")
		if max_volatility <= 0:
			raise ValueError("max_volatility must be positive")
		
		self.target_risk = float(target_risk)
		self.min_allocation = min_allocation
		self.max_allocation = max_allocation
		self.max_volatility = max_volatility

	def calculate(self, volatility: float) -> float:
		

		if not isinstance(volatility, (int, float)):
			raise TypeError("volatility must be a number")
		
		if volatility <= 0:
			logger.info("Allocation 0.0: volatility is %.4f, so there is no usable risk estimate", volatility)
			return 0.0

		if volatility > self.max_volatility:
			logger.info("Allocation 0.0: volatility %.4f is above max_volatility %.4f", volatility, self.max_volatility)
			return 0.0
		
		raw_allocation = self.target_risk / volatility
		allocation = min(raw_allocation, self.max_allocation)

		if raw_allocation > self.max_allocation:
			logger.debug("Allocation capped at max_allocation: wanted %.2f%%, using %.2f%%", raw_allocation * 100, allocation * 100)

		if allocation < self.min_allocation:
			logger.info("Allocation 0.0: %.2f%% is below min_allocation %.2f%%", allocation * 100, self.min_allocation * 100)
			return 0.0

		logger.debug("Allocation %.2f%% (volatility=%.4f, target_risk=%.4f)", allocation * 100, volatility, self.target_risk)

		return allocation
