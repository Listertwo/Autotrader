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
        tuple[pd.DataFrame, pd.Series, pd.Series]
            The DataFrame (with any indicator columns added), the buy mask,
            and the sell mask. The Signal column is not applied here -
            call apply_signals once a final buy/sell mask is ready.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def apply_signals(self, df, buy, sell):
        """
        Apply the generated signals to the DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        pd.DataFrame
            DataFrame with trading signals applied.
        """
        
        df["Signal"] = 0
        df.loc[buy, "Signal"] = 1
        df.loc[sell, "Signal"] = -1
        
        return df