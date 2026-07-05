def cross_over(fast: int, slow: int) -> bool:
     """
     Determines if a crossover has occurred between two moving averages.

     Parameters
     ----------
     fast : int
         The value of the fast moving average.
     slow : int
         The value of the slow moving average.

     Returns
     -------
     bool
         True if a crossover has occurred, False otherwise.
     """
     return fast > slow and fast.shift(1) <= slow.shift(1)

def cross_under(fast: int, slow: int) -> bool:
    """
    Determines if a crossunder has occurred between two moving averages.

    Parameters
    ----------
    fast : int
        The value of the fast moving average.
    slow : int
        The value of the slow moving average.

    Returns
    -------
    bool
        True if a crossunder has occurred, False otherwise.
    """
    return fast < slow and fast.shift(1) >= slow.shift(1)