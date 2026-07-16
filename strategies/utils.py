import pandas as pd


def cross_over(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Determines if a crossover has occurred between two moving averages.

    Parameters
    ----------
    series1 : pd.Series
        The value of the first data series.
    series2 : pd.Series
        The value of the second data series.

    Returns
    -------
    bool
        True if a crossover has occurred, False otherwise.
    """
    if not isinstance(series1, pd.Series) or not isinstance(series2, pd.Series):
        raise TypeError("Both series must be pandas Series")

    return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

def cross_under(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """
    Determines if a crossunder has occurred between two moving averages.

    Parameters
    ----------
    series1 : pd.Series
        The value of the first data series.
    series2 : pd.Series
        The value of the second data series.

    Returns
    -------
    bool
        True if a crossunder has occurred, False otherwise.
    """
    if not isinstance(series1, pd.Series) or not isinstance(series2, pd.Series):
        raise TypeError("Both series must be pandas Series")

    return (series1 < series2) & (series1.shift(1) >= series2.shift(1))

def cross_over_level(series: pd.Series, level: float):
    """
    Determine whether a time series crosses above a fixed level.

    Parameters
    ----------
    series : pd.Series
        The value of the data series.
    level : float
        The value of the risk index level.

    Returns
    -------
    bool
        True if a crossover has occurred, False otherwise.
    """
    if not isinstance(series, pd.Series):
        raise TypeError("series must be a pandas Series")
    if not isinstance(level, (int, float)):
        raise TypeError("level must be numeric")
    
    return (series > level) & (series.shift(1) <= level)

def cross_under_level(series: pd.Series, level: float):
    """
    Determine whether a time series crosses below a fixed level.

    Parameters
    ----------
    series : pd.Series
        The value of the data series.
    level : float
        The value of the risk index level.

    Returns
    -------
    bool
        True if a crossunder has occurred, False otherwise.
    """
    if not isinstance(series, pd.Series):
        raise TypeError("series must be a pandas Series")
    if not isinstance(level, (int, float)):
        raise TypeError("level must be numeric")
    
    return (series < level) & (series.shift(1) >= level)
