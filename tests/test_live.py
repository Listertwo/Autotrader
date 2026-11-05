"""
Live-data comparison (needs internet via yfinance; results are cached by your data/cache.py).

This is NOT pass/fail. It runs several strategies and engine settings on real data and prints
one comparison table, so you can see how each option changes the results.

Run from the project root:   python tests/test_live.py
Edit the SETTINGS block below to try other symbols / periods / options.
Add  --offline  to use synthetic data instead (just to check the script itself works).
"""
import sys
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from backtest.engine import BacktestEngine
from strategies.crossover import SmaCrossoverStrategy, EmaCrossoverStrategy
from strategies.momentum import RsiStrategy, MacdStrategy, MacdZeroLineStrategy, MacdHistogramStrategy

# ------------------------------------------------------------------ SETTINGS
SYMBOLS = ["AAPL", "NVDA", "MSFT"]          # try low-volatility names too: ["KO", "PG", "JNJ", "SPY"]
PERIOD = "1y"                               # try "2y" or "5y" for a fairer test
INTERVAL = "1d"

STRATEGIES = {
    "MACD": MacdStrategy,
    "MACD zero-line": MacdZeroLineStrategy,
    "MACD histogram": MacdHistogramStrategy,
    "SMA 10/30": lambda: SmaCrossoverStrategy(10, 30),
    "EMA 10/30": lambda: EmaCrossoverStrategy(10, 30),
    "RSI": RsiStrategy,
}

ENGINE_SETTINGS = {                          # name -> BacktestEngine options
    "default (cap 0.20)": dict(),
    "no vol cap": dict(max_volatility=5.0),
    "cap 0.40": dict(max_volatility=0.40),
    "big positions": dict(max_volatility=5.0, max_allocation=0.5),
    "with $1 fees": dict(max_volatility=5.0, commission=1.0),
    "60-day lookback": dict(max_volatility=5.0, lookback=60),
}
# ---------------------------------------------------------------------------


def load_data():
    if "--offline" in sys.argv:
        return make_universe(SYMBOLS, bars=250)
    from data.downloader import get_data
    return get_data(SYMBOLS, interval=INTERVAL, period=PERIOD)


def main():
    data = load_data()
    rows = []
    for engine_name, options in ENGINE_SETTINGS.items():
        for strategy_name, build in STRATEGIES.items():
            try:
                r = BacktestEngine(**options).run(build(), data)
            except Exception as e:
                rows.append((engine_name, strategy_name, f"ERROR: {e!r}"))
                continue
            rows.append((engine_name, strategy_name, r))

    header = f"{'engine settings':<20}{'strategy':<16}{'trades':>7}{'win%':>7}{'net $':>10}{'CAGR':>8}{'Sharpe':>8}{'maxDD':>8}{'expos.':>8}"
    print("\n" + header)
    print("-" * len(header))
    last = None
    for engine_name, strategy_name, r in rows:
        if last and engine_name != last:
            print()
        last = engine_name
        if isinstance(r, str):
            print(f"{engine_name:<20}{strategy_name:<16}{r}")
            continue
        print(f"{engine_name:<20}{strategy_name:<16}{r.trade_count:>7}{r.win_rate:>7.0%}{r.total_return:>10.2f}"
              f"{r.cagr:>8.1%}{r.sharpe_ratio:>8.2f}{r.max_drawdown:>8.1%}{r.exposure:>8.1%}")

    good = [x for x in rows if not isinstance(x[2], str)]
    if good:
        best = max(good, key=lambda x: x[2].total_return)
        print(f"\nBest net profit: {best[1]} with '{best[0]}' -> ${best[2].total_return:,.2f}")
    print("Reminder: one year on a few symbols is a small sample. Don't tune on it.")


if __name__ == "__main__":
    main()
