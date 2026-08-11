from strategies.base import Strategy
from indicators.basic import add_ema, add_sma
from strategies.utils import cross_over, cross_under

import pandas as pd

class SmaCrossoverStrategy(Strategy):
    """
    A simple moving average crossover strategy.
    """

    def __init__(self, fast: int, slow: int):
        super().__init__("SMA_Crossover")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Generate trading signals based on moving average crossovers.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        tuple[pd.DataFrame, pd.Series, pd.Series]
            The DataFrame, the buy mask, and the sell mask.
        """
        
        if self.fast >= self.slow:
            raise ValueError("Fast period must be less than slow period for crossover strategy.")
        if self.fast <= 0 or self.slow <= 0:
            raise ValueError("Fast and slow periods must be positive integers.")
        
        fast_col = f"SMA_{self.fast}_Close"
        slow_col = f"SMA_{self.slow}_Close"

        if fast_col not in df.columns or slow_col not in df.columns:
            df = add_sma(df, self.fast)
            df = add_sma(df, self.slow)

        fast = df[fast_col]
        slow = df[slow_col]

        buy = cross_over(fast, slow)
        sell = cross_under(fast, slow)

        return df, buy, sell

class EmaCrossoverStrategy(Strategy):
    """
    An exponential moving average crossover strategy.
    """

    def __init__(self, fast: int, slow: int):
        super().__init__("EMA_Crossover")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
        """
        Generate trading signals based on exponential moving average crossovers.

        Parameters
        ----------
        df : pd.DataFrame
            Historical market data.

        Returns
        -------
        tuple[pd.DataFrame, pd.Series, pd.Series]
            The DataFrame, the buy mask, and the sell mask.
        """
        
        if self.fast >= self.slow:
            raise ValueError("Fast period must be less than slow period for crossover strategy.")
        if self.fast <= 0 or self.slow <= 0:
            raise ValueError("Fast and slow periods must be positive integers.")
        
        fast_col = f"EMA_{self.fast}_Close"
        slow_col = f"EMA_{self.slow}_Close"

        if fast_col not in df.columns or slow_col not in df.columns:
            df = add_ema(df, self.fast)
            df = add_ema(df, self.slow)

        fast = df[fast_col]
        slow = df[slow_col]
        
        buy = cross_over(fast, slow)
        sell = cross_under(fast, slow)

        return df, buy, sell

