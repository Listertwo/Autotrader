"""Every strategy: signals are valid and each one survives a full backtest."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from backtest.engine import BacktestEngine
from strategies.crossover import SmaCrossoverStrategy, EmaCrossoverStrategy
from strategies.momentum import (
    RsiStrategy, RsiCenterlineStrategy,
    MacdStrategy, MacdZeroLineStrategy, MacdHistogramStrategy,
    StochasticStrategy, StochasticLevelStrategy, StochasticFilteredStrategy, StochasticCenterlineStrategy,
)
from strategies.trend import GoldenCrossStrategy

STRATEGIES = {
    "SMA 10/30": lambda: SmaCrossoverStrategy(fast=10, slow=30),
    "SMA 20/50": lambda: SmaCrossoverStrategy(fast=20, slow=50),
    "EMA 10/30": lambda: EmaCrossoverStrategy(fast=10, slow=30),
    "RSI default": lambda: RsiStrategy(),
    "RSI 7 (20/80)": lambda: RsiStrategy(period=7, oversold=20, overbought=80),
    "RSI centerline": lambda: RsiCenterlineStrategy(),
    "MACD": lambda: MacdStrategy(),
    "MACD fast (8/17/9)": lambda: MacdStrategy(fast=8, slow=17, signal=9),
    "MACD zero-line": lambda: MacdZeroLineStrategy(),
    "MACD histogram": lambda: MacdHistogramStrategy(),
    "Stochastic": lambda: StochasticStrategy(),
    "Stochastic level": lambda: StochasticLevelStrategy(),
    "Stochastic filtered": lambda: StochasticFilteredStrategy(),
    "Stochastic centerline": lambda: StochasticCenterlineStrategy(),
    "Golden cross (needs 200+ bars)": lambda: GoldenCrossStrategy(),
}

# Strategies that currently crash. Names listed here are skipped in the sweeps below so the
# other strategies still get tested. Keep this empty unless something is known to be broken.
KNOWN_BROKEN = set()


def working():
    return {n: b for n, b in STRATEGIES.items() if n not in KNOWN_BROKEN}


def test_every_strategy_returns_valid_signals():
    data = make_prices(seed=11, bars=400)
    for name, build in working().items():
        strategy = build()
        out = strategy.generate_signals(data.copy())
        assert isinstance(out, tuple) and len(out) == 3, f"{name}: must return (df, buy, sell)"
        df, buy, sell = out
        assert len(buy) == len(df) == len(sell), f"{name}: mask length"
        applied = strategy.apply_signals(df, buy, sell)
        assert set(applied["Signal"].unique()) <= {-1, 0, 1}, f"{name}: bad Signal values"
        if not name.startswith("Golden"):     # 200-bar warm-up leaves too little room for a cross on 400 bars
            assert (applied["Signal"] != 0).any(), f"{name}: produced no signals at all on 400 bars"


def test_every_strategy_survives_a_full_backtest():
    data = make_universe(bars=400)
    for name, build in working().items():
        results = BacktestEngine(max_volatility=5.0).run(build(), data)
        str(results)
        assert results.final_cash > 0, name


def test_signals_do_not_change_original_price_columns():
    data = make_prices(seed=4, bars=300)
    for name, build in working().items():
        df, buy, sell = build().generate_signals(data.copy())
        assert df["Close"].equals(data["Close"]), f"{name} altered Close"


def test_short_data_does_not_crash():
    short = make_prices(seed=2, bars=40)
    for name, build in working().items():
        try:
            BacktestEngine(max_volatility=5.0).run(build(), {"AAA": short})
        except Exception as e:
            raise AssertionError(f"{name} crashed on 40 bars: {e!r}")


def test_stochastic_columns_match_the_indicator():
    """
    Regression test for a bug: the Stochastic strategies once looked for 'Stochastic_%K_<k>_Close'
    while add_stochastic() creates 'Stochastic_%K_<period>_<smooth>' (e.g. 'Stochastic_%K_14_3'),
    so every Stochastic strategy raised KeyError. Try non-default periods too, since both
    numbers appear in the column names.
    """
    data = make_prices(seed=11, bars=400)
    for k_period, d_period in [(14, 3), (9, 5), (5, 2)]:
        for cls in (StochasticStrategy, StochasticLevelStrategy, StochasticFilteredStrategy, StochasticCenterlineStrategy):
            df, buy, sell = cls(k_period=k_period, d_period=d_period).generate_signals(data.copy())
            assert f"Stochastic_%K_{k_period}_{d_period}" in df.columns, (cls.__name__, k_period, d_period)
            assert len(buy) == len(df) == len(sell)


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Strategies") else 0)
