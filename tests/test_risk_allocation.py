"""Risk (volatility) and Allocator (position sizing)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from risk.riskclass import Risk
from risk.allocation import Allocator


def raises(exc, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except exc:
        return True
    return False


# ---------------------------------------------------------------- Allocator
def test_allocator_unknown_risk_gives_zero():
    assert Allocator().calculate(0.0) == 0.0
    assert Allocator().calculate(-0.1) == 0.0


def test_allocator_above_max_volatility_gives_zero():
    assert Allocator(max_volatility=0.30).calculate(0.31) == 0.0
    assert Allocator(max_volatility=0.30).calculate(0.30) > 0.0     # exactly at the limit is allowed


def test_allocator_formula_and_cap():
    a = Allocator(target_risk=0.02, max_allocation=0.25, max_volatility=1.0)
    assert abs(a.calculate(0.10) - 0.20) < 1e-9       # 0.02 / 0.10
    assert abs(a.calculate(0.05) - 0.25) < 1e-9       # 0.40 capped to 0.25


def test_allocator_min_allocation():
    a = Allocator(target_risk=0.02, min_allocation=0.30, max_allocation=0.50, max_volatility=1.0)
    assert a.calculate(0.10) == 0.0                   # 0.20 < 0.30 -> skip trade
    assert abs(a.calculate(0.04) - 0.50) < 1e-9


def test_allocator_higher_volatility_means_smaller_position():
    a = Allocator(max_allocation=1.0, max_volatility=2.0)
    assert a.calculate(0.1) > a.calculate(0.2) > a.calculate(0.4)


def test_allocator_validation():
    assert raises(ValueError, Allocator, target_risk=0)
    assert raises(ValueError, Allocator, min_allocation=-0.1)
    assert raises(ValueError, Allocator, max_allocation=0.0)
    assert raises(ValueError, Allocator, min_allocation=0.5, max_allocation=0.4)
    assert raises(ValueError, Allocator, max_volatility=0.0)
    assert raises(TypeError, Allocator, max_allocation="big")
    assert raises(TypeError, Allocator().calculate, "high") is True


# --------------------------------------------------------------------- Risk
def test_risk_matches_manual_calculation():
    df = make_prices(seed=5, bars=100)
    date = df.index[60]
    manual = df["Close"].pct_change()[df.index < date].std() * np.sqrt(252)
    assert abs(Risk().volatility(df, date) - manual) < 1e-12


def test_risk_not_annualized():
    df = make_prices(seed=5, bars=100)
    date = df.index[60]
    assert abs(Risk(annualize=False).volatility(df, date) * np.sqrt(252) - Risk().volatility(df, date)) < 1e-12


def test_risk_has_no_lookahead():
    """Volatility 'as of' a date must not change if future rows are removed or altered."""
    df = make_prices(seed=7, bars=150)
    date = df.index[80]
    full = Risk().volatility(df, date)
    truncated = Risk().volatility(df.loc[df.index < date], date)
    tampered = df.copy()
    tampered.loc[tampered.index >= date, "Close"] *= 10
    assert abs(full - truncated) < 1e-12
    assert abs(full - Risk().volatility(tampered, date)) < 1e-12


def test_risk_short_history_returns_zero():
    df = make_prices(seed=1, bars=100)
    assert Risk().volatility(df, df.index[10]) == 0.0           # fewer than 20 returns
    assert Risk(lookback=50).volatility(df, df.index[30]) == 0.0


def test_risk_lookback_uses_only_recent_window():
    df = make_prices(seed=2, bars=200)
    date = df.index[150]
    returns = df["Close"].pct_change()[df.index < date].tail(30)
    assert abs(Risk(lookback=30).volatility(df, date) - returns.std() * np.sqrt(252)) < 1e-12


def test_risk_does_not_modify_input():
    df = make_prices(seed=3, bars=100)
    before = list(df.columns)
    Risk().volatility(df, df.index[60])
    assert list(df.columns) == before


def test_risk_validation():
    assert raises(TypeError, Risk, annualize="yes")
    assert raises(ValueError, Risk, trading_periods=0)
    assert raises(ValueError, Risk, lookback=1)
    assert raises(TypeError, Risk, lookback=2.5)


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Risk & Allocator") else 0)
