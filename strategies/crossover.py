from strategies.base import Strategy
from indicators.basic import add_ema, add_sma
from strategies.utils import cross_over, cross_under

import pandas as pd

class SmaCrossoverStrategy(Strategy):
    """
    A simple moving average crossover strategy.
    """

    default_params = {"fast": 10, "slow": 30}

    def validate(self):
        if self.params["fast"] >= self.params["slow"]:
            raise ValueError("fast must be shorter than slow")
    
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

        fast = self.params["fast"]
        slow = self.params["slow"]
        
        if fast >= slow:
            raise ValueError("Fast period must be less than slow period for crossover strategy.")
        if fast <= 0 or slow <= 0:
            raise ValueError("Fast and slow periods must be positive integers.")
        
        fast_col = f"SMA_{fast}_Close"
        slow_col = f"SMA_{slow}_Close"

        if fast_col not in df.columns or slow_col not in df.columns:
            df = add_sma(df, fast)
            df = add_sma(df, slow)

        fast_df = df[fast_col]
        slow_df = df[slow_col]

        buy = cross_over(fast_df, slow_df)
        sell = cross_under(fast_df, slow_df)

        return df, buy, sell

class EmaCrossoverStrategy(Strategy):
    """
    An exponential moving average crossover strategy.
    """

    default_params = {"fast": 10, "slow": 30}

    def validate(self):
        if self.params["fast"] >= self.params["slow"]:
            raise ValueError("fast must be shorter than slow")

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

        fast = self.params["fast"]
        slow = self.params["slow"]
        
        if fast >= slow:
            raise ValueError("Fast period must be less than slow period for crossover strategy.")
        if fast <= 0 or slow <= 0:
            raise ValueError("Fast and slow periods must be positive integers.")
        
        fast_col = f"EMA_{fast}_Close"
        slow_col = f"EMA_{slow}_Close"

        if fast_col not in df.columns or slow_col not in df.columns:
            df = add_ema(df, fast)
            df = add_ema(df, slow)

        fast_df = df[fast_col]
        slow_df = df[slow_col]
        
        buy = cross_over(fast_df, slow_df)
        sell = cross_under(fast_df, slow_df)

        return df, buy, sell

