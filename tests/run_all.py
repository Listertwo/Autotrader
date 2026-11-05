"""Run every offline test file. Usage (from the project root):  python -m tests.run_all   (or python tests/run_all.py)"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import run_tests

FILES = ["test_portfolio", "test_risk_allocation", "test_engine", "test_results", "test_strategies", "test_logger", "test_cache"]

failed = 0
for name in FILES:
    module = importlib.import_module(f"tests.{name}")
    failed += run_tests(vars(module), name)

print("\nALL OFFLINE TESTS PASSED" if not failed else f"\n{failed} TEST(S) FAILED")
sys.exit(1 if failed else 0)
