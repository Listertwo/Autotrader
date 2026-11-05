"""
Engine: end-to-end backtests on synthetic data with many option combinations.
Every combination must satisfy the same invariants (see check_invariants).
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from backtest.engine import BacktestEngine
from strategies.base import Strategy
from strategies.momentum import MacdStrategy


class ScriptedStrategy(Strategy):
    """Fires exactly the signals you give it: {bar_number: 1 or -1}. Makes tests predictable."""
    def __init__(self, script):
        super().__init__("Scripted")
        self.script = script

    def generate_signals(self, df):
        buy = pd.Series(False, index=df.index)
        sell = pd.Series(False, index=df.index)
        for bar, sig in self.script.items():
            (buy if sig == 1 else sell).iloc[bar] = True
        return df.copy(), buy, sell


def run_engine(strategy, data, **options):
    """Run the engine and also return the Portfolio (BacktestResults hides it)."""
    import backtest.engine as engine_module
    captured = {}
    original = engine_module.BacktestResults.from_portfolio
    engine_module.BacktestResults.from_portfolio = staticmethod(lambda p: captured.setdefault("p", p) and original(p))
    try:
        results = BacktestEngine(**options).run(strategy, data)
    finally:
        engine_module.BacktestResults.from_portfolio = original
    return results, captured["p"]


def check_invariants(portfolio, label=""):
    msg = f" [{label}]"
    assert books_balance(portfolio), "profits don't match cash change" + msg
    assert all(p["shares"] == 0 for p in portfolio.positions.values()), "positions left open" + msg
    assert portfolio.cash >= -1e-6, "negative cash" + msg
    for s in portfolio.history:
        assert abs(s.equity - (s.cash + s.market_value)) < 1e-6, "equity != cash + market value" + msg
        assert s.cash >= -1e-6, "negative cash in snapshot" + msg
    for t in portfolio.trades:
        assert t.exit_date >= t.entry_date and t.shares > 0, "bad trade" + msg
    dates = [s.date for s in portfolio.history]
    assert dates == sorted(dates) and len(dates) == len(set(dates)), "snapshots out of order" + msg


# ------------------------------------------------------------- option sweep
def test_option_sweep_invariants():
    data = make_universe(bars=300)
    grid = itertools.product(
        [1_000, 10_000, 1_000_000],          # initial_cash
        [0.0, 1.0, 5.0],                     # commission
        [0.01, 0.05],                        # target_risk
        [0.10, 0.50, 1.0],                   # max_allocation
        [None, 30],                          # lookback
    )
    count = 0
    for cash, fee, risk, max_alloc, lookback in grid:
        _, p = run_engine(MacdStrategy(), data, initial_cash=cash, commission=fee, target_risk=risk,
                          min_allocation=0.0, max_allocation=max_alloc, max_volatility=2.0, lookback=lookback)
        check_invariants(p, f"cash={cash} fee={fee} risk={risk} max_alloc={max_alloc} lookback={lookback}")
        count += 1
    assert count == 108


def test_annualize_off_and_trading_periods():
    data = make_universe()
    for annualize, periods in [(True, 252), (False, 252), (True, 365)]:
        _, p = run_engine(MacdStrategy(), data, annualize=annualize, trading_periods=periods, max_volatility=2.0)
        check_invariants(p, f"annualize={annualize} periods={periods}")


def test_single_symbol_and_many_symbols():
    one = {"AAA": make_prices(seed=1)}
    many = make_universe(symbols=[f"S{i}" for i in range(8)])
    for data in (one, many):
        _, p = run_engine(MacdStrategy(), data, max_volatility=2.0)
        check_invariants(p, f"{len(data)} symbols")


def test_deterministic():
    data = make_universe()
    a, _ = run_engine(MacdStrategy(), data, max_volatility=2.0)
    b, _ = run_engine(MacdStrategy(), data, max_volatility=2.0)
    assert a.total_return == b.total_return and a.trade_count == b.trade_count


def test_input_data_not_corrupted():
    data = make_universe()
    before = {s: df.copy() for s, df in data.items()}
    run_engine(MacdStrategy(), data, max_volatility=2.0)
    for s in data:
        assert list(data[s].index) == list(before[s].index)
        assert data[s]["Close"].equals(before[s]["Close"])


# ------------------------------------------------------------- risk wiring
def test_volatility_cap_blocks_trades():
    data = make_universe(daily_vol=0.03)         # ~48% annualized
    _, blocked = run_engine(MacdStrategy(), data, max_volatility=0.10)
    _, allowed = run_engine(MacdStrategy(), data, max_volatility=5.0)
    assert len(blocked.trades) == 0
    assert len(allowed.trades) > 0


def test_max_allocation_respected():
    data = make_universe()
    _, p = run_engine(ScriptedStrategy({40: 1, 80: -1}), data, max_allocation=0.10, max_volatility=5.0, target_risk=0.5)
    assert len(p.trades) == 3
    for t in p.trades:
        before = [s.equity for s in p.history if s.date < t.entry_date]
        equity = before[-1] if before else p.initial_cash
        assert t.shares * t.entry_price <= 0.10 * equity + 1e-6


def test_higher_volatility_symbol_gets_smaller_position():
    data = {"CALM": make_prices(seed=1, daily_vol=0.005), "WILD": make_prices(seed=1, daily_vol=0.02)}
    _, p = run_engine(ScriptedStrategy({60: 1, 100: -1}), data, max_allocation=1.0, max_volatility=5.0, target_risk=0.02)
    value = {t.trade_symbol: t.shares * t.entry_price for t in p.trades}
    assert value["CALM"] > value["WILD"]


def test_no_trades_before_enough_history():
    data = make_universe()
    _, p = run_engine(ScriptedStrategy({5: 1, 50: -1}), data, max_volatility=5.0)
    # a buy at bar 5 has < 20 days of returns -> volatility 0.0 -> allocation 0.0 -> skipped
    assert all(t.entry_date >= data["AAA"].index[20] for t in p.trades)


# --------------------------------------------------- sell-before-buy ordering
def test_sells_processed_before_buys_on_same_day():
    """
    'B' is listed first, so its BUY event sits before 'A's SELL event on day 100.
    With a correct two-pass loop, A's sale cash is available to B.
    """
    idx = make_prices(seed=1).index
    data = {"B": make_prices(seed=2), "A": make_prices(seed=1)}

    class Script(Strategy):
        def __init__(self):
            super().__init__("Script")
        def generate_signals(self, df):
            buy = pd.Series(False, index=df.index); sell = pd.Series(False, index=df.index)
            is_a = df["Close"].equals(data["A"]["Close"])
            if is_a:
                buy.iloc[40] = True; sell.iloc[100] = True      # A: buy bar 40, sell bar 100
            else:
                buy.iloc[100] = True                            # B: buy the same bar A sells
            return df.copy(), buy, sell

    _, p = run_engine(Script(), data, max_allocation=1.0, target_risk=5.0, max_volatility=5.0)
    b = [t for t in p.trades if t.trade_symbol == "B"][0]
    equity_before = [s.equity for s in p.history if s.date < b.entry_date][-1]
    assert b.shares * b.entry_price > 0.9 * equity_before, "B was starved of cash: sells must run before buys"


# ------------------------------------------------------------- input checks
def test_input_validation():
    for bad in (["AAA"], None, "AAA"):
        try:
            BacktestEngine().run(MacdStrategy(), bad)
            raise AssertionError("expected TypeError")
        except TypeError:
            pass
    for bad in ({1: make_prices()}, {"AAA": [1, 2, 3]}):
        try:
            BacktestEngine().run(MacdStrategy(), bad)
            raise AssertionError("expected TypeError")
        except TypeError:
            pass


def test_no_signals_means_no_trades_and_clean_results():
    results, p = run_engine(ScriptedStrategy({}), make_universe(), max_volatility=5.0)
    assert results.trade_count == 0 and results.final_cash == results.initial_cash
    str(results)


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Engine") else 0)
