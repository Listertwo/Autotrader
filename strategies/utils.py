def cross_over(series1: int, series2: int) -> bool:
     """
     Determines if a crossover has occurred between two moving averages.

     Parameters
     ----------
     series1 : int
         The value of the first data series.
     series2 : int
         The value of the second data series.

     Returns
     -------
     bool
         True if a crossover has occurred, False otherwise.
     """
     return series1 > series2 and series1.shift(1) <= series2.shift(1)

def cross_under(series1: int, series2: int) -> bool:
    """
    Determines if a crossunder has occurred between two moving averages.

    Parameters
    ----------
    series1 : int
        The value of the first data series.
    series2 : int
        The value of the second data series.

    Returns
    -------
    bool
        True if a crossunder has occurred, False otherwise.
    """
    return series1 < series2 and series1.shift(1) >= series2.shift(1)

def cross_over_level(series: int, level: int):
    """
    Determines if a crossover has occurred between two moving averages.

    Parameters
    ----------
    series : int
        The value of the data series.
    series2 : int
        The value of the risk index level.

    Returns
    -------
    bool
        True if a crossover has occurred, False otherwise.
    """

	return series > level and series.shift(1) <= level.shift(1)

def cross_under_level(series: int, level: int):
    """
    Determines if a crossunder has occurred between two moving averages.

    Parameters
    ----------
    series : int
        The value of the data series.
    series2 : int
        The value of the risk index level.

    Returns
    -------
    bool
        True if a crossunder has occurred, False otherwise.
    """

	return series < level and series.shift(1) >= level.shift(1)
