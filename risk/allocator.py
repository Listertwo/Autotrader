class Allocator:
    def __init__(self, target_risk: float):
        self.target_risk = target_risk

    def calculate(self, volatility: float) -> float:
        """
        Calculate the allocation based on the target risk and current volatility.

        Parameters
        ----------
        volatility : float
            The current volatility of the asset.

        Returns
        -------
        float
            The allocation percentage (between 0 and 1).
        """
        if volatility <= 0:
            raise ValueError("Volatility must be greater than zero to calculate allocation.")

        allocation = self.target_risk / volatility

        # Ensure allocation is between 0 and 1
        allocation = max(0, min(allocation, 1))

        return allocation