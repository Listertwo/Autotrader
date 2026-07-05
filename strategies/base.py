from abc import ABC, abstractmethod

class Strategy(ABC):
    """
    Base class for trading strategies.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, df):
        """
        Generate trading signals based on the strategy.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        pd.DataFrame
            DataFrame with trading signals.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")