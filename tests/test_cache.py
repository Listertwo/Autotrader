"""
Cache: every distinct request gets its own cache file, and a cached answer is never served for a
different request. Uses a temporary cache folder and a fake downloader, so nothing touches the
internet or your real cache.
"""
import os
import sys
import tempfile
import types
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *

try:
    import yfinance  # noqa: F401  (real one, if installed)
except ImportError:
    sys.modules["yfinance"] = types.ModuleType("yfinance")      # not needed here: the download is faked below

import data.cache as cache
import data.downloader as downloader


class FakeMarket:
    """Replaces download_data and the cache folder for the duration of one test."""
    def __init__(self):
        self.calls = []

    def download(self, symbol, start=None, end=None, period="1y", interval="1d"):
        self.calls.append((symbol, start, end, period, interval))
        first = pd.Timestamp(start) if start else pd.Timestamp("2025-01-02")
        last = pd.Timestamp(end) if end else first + pd.Timedelta(days=364)
        bars = len(pd.bdate_range(first, last))
        df = make_prices(seed=len(self.calls), bars=bars, start=first)
        return df

    def __enter__(self):
        self._dir = tempfile.TemporaryDirectory()
        self._old = (cache.CACHE_DIR, downloader.download_data)
        cache.CACHE_DIR = __import__("pathlib").Path(self._dir.name)
        downloader.download_data = self.download
        return self

    def __exit__(self, *exc):
        cache.CACHE_DIR, downloader.download_data = self._old
        self._dir.cleanup()

    def files(self):
        return sorted(os.listdir(self._dir.name))


A_START, A_END = datetime(2020, 1, 1), datetime(2020, 12, 31)
B_START, B_END = datetime(2022, 1, 1), datetime(2022, 12, 30)


# -------------------------------------------------------------- the original bug
def test_different_date_ranges_are_not_served_each_others_data():
    with FakeMarket() as market:
        a = downloader.get_data(["AAPL"], start=A_START, end=A_END)["AAPL"]
        b = downloader.get_data(["AAPL"], start=B_START, end=B_END)["AAPL"]
        assert len(market.calls) == 2, "second range must trigger its own download"
        assert a.index.min() >= pd.Timestamp(A_START) and a.index.max() <= pd.Timestamp(A_END)
        assert b.index.min() >= pd.Timestamp(B_START) and b.index.max() <= pd.Timestamp(B_END)
        assert not a.index.equals(b.index)


def test_period_request_and_range_request_do_not_collide():
    with FakeMarket() as market:
        downloader.get_data(["AAPL"], period="1y")
        ranged = downloader.get_data(["AAPL"], start=A_START, end=A_END)["AAPL"]
        assert len(market.calls) == 2
        assert ranged.index.min() >= pd.Timestamp(A_START)
        assert len(market.files()) == 2


# ----------------------------------------------------------- caching still works
def test_same_request_twice_downloads_once():
    with FakeMarket() as market:
        first = downloader.get_data(["AAPL"], start=A_START, end=A_END)["AAPL"]
        second = downloader.get_data(["AAPL"], start=A_START, end=A_END)["AAPL"]
        assert len(market.calls) == 1, "second identical request should come from the cache"
        assert len(first) == len(second)

    with FakeMarket() as market:
        downloader.get_data(["AAPL"], period="1y")
        downloader.get_data(["AAPL"], period="1y")
        assert len(market.calls) == 1


def test_symbols_and_intervals_get_separate_files():
    with FakeMarket() as market:
        downloader.get_data(["AAPL", "MSFT"], period="1y")
        downloader.get_data(["AAPL"], period="1y", interval="1wk")
        assert market.files() == ["AAPL_1y_1d.csv", "AAPL_1y_1wk.csv", "MSFT_1y_1d.csv"]
        assert len(market.calls) == 3


def test_period_is_ignored_when_dates_are_given():
    """With start/end set, yfinance ignores the period, so 1y and 5y are the same request."""
    with FakeMarket() as market:
        downloader.get_data(["AAPL"], start=A_START, end=A_END, period="1y")
        downloader.get_data(["AAPL"], start=A_START, end=A_END, period="5y")
        assert len(market.calls) == 1


# -------------------------------------------------------------------- file names
def test_cache_file_names():
    name = cache.get_cache_name
    assert name("AAPL", "1y", "1d") == "AAPL_1y_1d.csv"
    assert name("AAPL", "1y", "1d", A_START, A_END) == "AAPL_2020-01-01_2020-12-31_1d.csv"
    assert name("AAPL", "1y", "1d", start=A_START) == "AAPL_2020-01-01_latest_1d.csv"
    assert name("AAPL", "1y", "1d", end=A_END) == "AAPL_begin_2020-12-31_1d.csv"


def test_intraday_names_have_no_characters_windows_rejects():
    n = cache.get_cache_name("AAPL", "1d", "5m", datetime(2024, 1, 2, 9, 30), datetime(2024, 1, 2, 16, 0))
    assert n == "AAPL_2024-01-02T0930_2024-01-02T1600_5m.csv"
    assert not any(ch in n for ch in '<>:"/\\|?*')


def test_different_requests_never_share_a_name():
    requests = [
        ("AAPL", "1y", "1d", None, None), ("AAPL", "5y", "1d", None, None), ("AAPL", "1y", "1wk", None, None),
        ("MSFT", "1y", "1d", None, None), ("AAPL", "1y", "1d", A_START, A_END), ("AAPL", "1y", "1d", B_START, B_END),
        ("AAPL", "1y", "1d", A_START, None), ("AAPL", "1y", "1d", None, A_END),
    ]
    names = [cache.get_cache_name(*r) for r in requests]
    assert len(set(names)) == len(requests)


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Cache") else 0)
