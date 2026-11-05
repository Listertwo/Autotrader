"""
Shared helpers for the AutoTrader test files.

Every test file imports this first. It:
  - puts the project root on sys.path so `import backtest...` works,
  - switches to the project root so the logger's relative `logs/` paths work,
  - quiets the console logger (the full detail still goes to logs/application.log),
  - provides synthetic price data so tests never need the internet,
  - provides a tiny test runner so you don't need pytest (pytest also works).
"""
import logging
import math
import os
import sys
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)

import numpy as np
import pandas as pd

from utils.logger import logger

# Silence console output while testing. The log FILES still get everything.
logging.getLogger().setLevel(logging.CRITICAL)
logger.setLevel(logging.CRITICAL)      # the project logger has its own level, so quiet it too
for _handler in logger.handlers:
    if type(_handler) is logging.StreamHandler:
        _handler.setLevel(logging.CRITICAL)


def make_prices(seed=0, bars=300, daily_vol=0.012, drift=0.0003, start="2025-01-01", start_price=100.0):
    """Synthetic OHLCV data (random walk). Same seed -> same data."""
    rng = np.random.default_rng(seed)
    close = start_price * np.cumprod(1 + rng.normal(drift, daily_vol, bars))
    index = pd.date_range(start, periods=bars, freq="B")
    return pd.DataFrame(
        {
            "Open": close * (1 + rng.normal(0, 0.002, bars)),
            "High": close * 1.01,
            "Low": close * 0.99,
            "Close": close,
            "Volume": 1_000_000.0,
        },
        index=index,
    )


def make_universe(symbols=("AAA", "BBB", "CCC"), bars=300, daily_vol=0.012):
    return {s: make_prices(seed=i + 1, bars=bars, daily_vol=daily_vol) for i, s in enumerate(symbols)}


def books_balance(portfolio, tol=1e-6):
    """Sum of trade profits must equal final cash - initial cash (once everything is closed)."""
    return abs(sum(t.profit for t in portfolio.trades) - (portfolio.cash - portfolio.initial_cash)) < tol


def is_bad_number(x):
    return isinstance(x, float) and math.isnan(x)


def run_tests(namespace, title):
    """Run every function named test_* in `namespace`, print PASS/FAIL, return failure count."""
    tests = [(n, f) for n, f in namespace.items() if n.startswith("test_") and callable(f)]
    failed = 0
    print(f"\n=== {title} ({len(tests)} tests) ===")
    for name, func in tests:
        try:
            func()
            print(f"  PASS  {name}")
        except Exception:
            failed += 1
            print(f"  FAIL  {name}")
            traceback.print_exc()
    print(f"--- {len(tests) - failed}/{len(tests)} passed")
    return failed
