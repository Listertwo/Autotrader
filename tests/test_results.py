"""BacktestResults: statistics on normal runs and on awkward edge cases."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from backtest.portfolio import Portfolio
from models.results import BacktestResults

DAYS = pd.date_range("2026-01-01", periods=60, freq="B")


def build(trade_script, equity_path=None):
    """trade_script: list of (buy_day_index, sell_day_index, buy_price, sell_price)."""
    p = Portfolio(10000)
    events = {}
    for sym_i, (b, s, bp, sp) in enumerate(trade_script):
        events.setdefault(b, []).append(("buy", f"S{sym_i}", bp))
        events.setdefault(s, []).append(("sell", f"S{sym_i}", sp))
    prices = {}
    for i, day in enumerate(DAYS):
        for kind, sym, price in events.get(i, []):
            prices[sym] = price
            if kind == "sell":
                p.sell(sym, day, price)
        for kind, sym, price in events.get(i, []):
            if kind == "buy":
                p.buy(sym, day, price, 0.20)
        p.snapshot(day, prices or {"X": 1.0})
    p.close(DAYS[-1], prices)
    return p


def numeric_fields(r):
    skip = {"trades", "winning_trades", "losing_trades", "drawdown", "sharpe_rating", "profit_rating"}
    return {k: v for k, v in vars(r).items() if k not in skip}


def assert_no_nan(r):
    for k, v in numeric_fields(r).items():
        assert not (isinstance(v, float) and math.isnan(v)), f"{k} is NaN"


def test_empty_portfolio():
    r = BacktestResults.from_portfolio(Portfolio(10000))
    assert_no_nan(r)
    assert r.trade_count == 0 and r.sharpe_rating == "N/A" and r.profit_rating == "N/A"
    str(r)


def test_history_but_no_trades():
    p = Portfolio(10000)
    p.snapshot(DAYS[0], {"A": 100.0}); p.snapshot(DAYS[1], {"A": 101.0})
    r = BacktestResults.from_portfolio(p)
    assert_no_nan(r)
    assert r.exposure == 0.0 and r.max_drawdown == 0.0 and r.recovery == 0.0
    str(r)


def test_single_winning_trade():
    r = BacktestResults.from_portfolio(build([(5, 30, 100.0, 120.0)]))
    assert_no_nan(r)
    assert r.trade_count == 1 and r.wins == 1 and r.losses == 0 and r.win_rate == 1.0
    assert r.total_return > 0 and r.largest_win == r.total_return
    assert r.profit_factor == float("inf")           # no losses at all
    str(r)


def test_single_losing_trade():
    r = BacktestResults.from_portfolio(build([(5, 30, 100.0, 80.0)]))
    assert_no_nan(r)
    assert r.losses == 1 and r.wins == 0 and r.win_rate == 0.0
    assert r.profit_factor == 0.0 and r.profit_rating == "Losing"
    assert r.max_drawdown < 0 and r.recovery < 0     # lost money: negative recovery
    str(r)


def test_mixed_trades_statistics():
    r = BacktestResults.from_portfolio(build([(5, 20, 100.0, 120.0), (25, 40, 100.0, 90.0), (42, 55, 50.0, 60.0)]))
    assert_no_nan(r)
    assert r.trade_count == 3 and r.wins == 2 and r.losses == 1
    assert abs(r.win_rate - 2 / 3) < 1e-9
    assert abs(r.total_return - sum(t.profit for t in r.trades)) < 1e-9
    assert abs(r.gross_profit - sum(t.profit for t in r.winning_trades)) < 1e-9
    assert abs(r.profit_factor - r.gross_profit / r.gross_loss) < 1e-9
    assert abs(r.final_cash - r.initial_cash - r.total_return) < 1e-6
    assert r.largest_win >= r.average_win > 0 > r.average_loss >= r.largest_loss
    assert r.shortest_holding <= r.average_holding <= r.longest_holding


def test_break_even_trade_is_neither_win_nor_loss():
    r = BacktestResults.from_portfolio(build([(5, 20, 100.0, 100.0)]))
    assert r.wins == 0 and r.losses == 0 and r.winning_trades == []


def test_exposure_is_between_zero_and_one_even_with_overlap():
    # three positions open at the same time for most of the run
    r = BacktestResults.from_portfolio(build([(2, 55, 100.0, 105.0), (3, 55, 50.0, 55.0), (4, 55, 20.0, 22.0)]))
    assert 0.0 < r.exposure <= 1.0, r.exposure


def test_recovery_sign_and_units():
    winner = BacktestResults.from_portfolio(build([(5, 20, 100.0, 120.0), (25, 30, 100.0, 90.0)]))
    assert winner.max_drawdown <= 0
    if winner.max_drawdown < 0:
        net_return = winner.final_cash / winner.initial_cash - 1
        assert abs(winner.recovery - net_return / abs(winner.max_drawdown)) < 1e-9


def test_printing_works():
    r = BacktestResults.from_portfolio(build([(5, 20, 100.0, 120.0)]))
    text = str(r)
    assert "BACKTEST RESULTS" in text and "Recovery Factor" in text
    r.print_trades()


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Results") else 0)
