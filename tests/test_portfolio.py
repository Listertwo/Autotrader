"""Portfolio: buying, selling, fees, closing, snapshots, drawdowns."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root, so "tests.x" and "backtest.x" imports work
from tests._helpers import *
from backtest.portfolio import Portfolio

D0, D1, D2 = pd.Timestamp("2026-01-02"), pd.Timestamp("2026-01-05"), pd.Timestamp("2026-01-09")


def raises(exc, func, *args):
    try:
        func(*args)
    except exc:
        return True
    return False


def test_buy_sizes_by_allocation():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.20)
    assert abs(p.positions["AAA"]["shares"] - 20.0) < 1e-9      # 20% of 10k = 2000 / 100
    assert abs(p.cash - 8000.0) < 1e-9


def test_buy_capped_by_cash():
    p = Portfolio(1000)
    p.buy("AAA", D0, 100.0, 5.0)           # asks for 500% of equity
    assert p.cash >= -1e-9                  # never goes negative
    assert abs(p.cash) < 1e-9               # spent everything available


def test_zero_allocation_does_nothing_and_charges_no_fee():
    p = Portfolio(10000, commission=5.0)
    p.buy("AAA", D0, 100.0, 0.0)
    assert p.cash == 10000
    assert p.positions["AAA"]["shares"] == 0


def test_buy_when_already_open_is_ignored():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.10)
    cash_after_first = p.cash
    p.buy("AAA", D1, 110.0, 0.10)
    assert p.cash == cash_after_first


def test_bad_price_raises():
    p = Portfolio(10000)
    assert raises(ValueError, p.buy, "AAA", D0, 0.0, 0.1)
    assert raises(ValueError, p.buy, "AAA", D0, -5.0, 0.1)
    assert raises(ValueError, p.sell, "AAA", D0, 0.0)


def test_sell_without_position_is_ignored():
    p = Portfolio(10000)
    p.sell("AAA", D0, 100.0)               # never traded
    p.buy("BBB", D0, 100.0, 0.1)
    p.sell("AAA", D1, 100.0)
    assert p.trades == []
    assert p.cash == 10000 - 1000


def test_round_trip_profit_no_fee():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.50)          # 50 shares
    p.sell("AAA", D1, 110.0)
    t = p.trades[0]
    assert t.symbol == "AAA"
    assert abs(t.profit - 500.0) < 1e-9
    assert abs(t.return_pct - 10.0) < 1e-9
    assert t.holding_period == 3
    assert abs(p.cash - 10500.0) < 1e-9


def test_round_trip_with_commission():
    p = Portfolio(10000, commission=10.0)
    p.buy("AAA", D0, 100.0, 0.50)          # fee 10, then 50% of equity (10000) = 5000 -> 50 shares
    p.sell("AAA", D1, 110.0)               # proceeds 5500 - 10
    t = p.trades[0]
    assert t.commission == 20.0                                  # buy fee + sell fee
    expected_profit = (50 * 110 - 10) - (50 * 100 + 10)          # proceeds - cost basis
    assert abs(t.profit - expected_profit) < 1e-9
    assert books_balance(p)


def test_sell_adds_to_cash_not_overwrites():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.10)           # 10% of 10000 = 1000 -> cash 9000
    p.buy("BBB", D0, 100.0, 0.10)           # no snapshot yet, so sized off cash: 10% of 9000 = 900 -> cash 8100
    p.sell("AAA", D1, 100.0)                # +1000 back
    assert abs(p.cash - 9100.0) < 1e-9      # BBB still open


def test_position_resets_after_sell_and_can_rebuy():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.10)
    p.sell("AAA", D1, 100.0)
    assert p.positions["AAA"]["shares"] == 0
    p.buy("AAA", D2, 100.0, 0.10)
    assert p.positions["AAA"]["shares"] > 0


def test_close_sells_everything_at_given_prices():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.10)
    p.buy("BBB", D0, 50.0, 0.10)
    p.close(D2, {"AAA": 120.0, "BBB": 40.0})
    assert len(p.trades) == 2
    assert all(pos["shares"] == 0 for pos in p.positions.values())
    assert books_balance(p)


def test_close_missing_price_raises():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.10)
    assert raises(ValueError, p.close, D2, {})


def test_snapshot_equity_and_independence():
    p = Portfolio(10000)
    p.buy("AAA", D0, 100.0, 0.50)                 # 50 shares, cash 5000
    p.snapshot(D0, {"AAA": 100.0})
    p.sell("AAA", D1, 120.0)
    p.snapshot(D1, {"AAA": 120.0})
    first, second = p.history
    assert abs(first.equity - 10000.0) < 1e-9
    assert abs(first.market_value - 5000.0) < 1e-9
    assert first.positions["AAA"]["shares"] == 50       # old snapshot NOT changed by the later sell
    assert second.positions["AAA"]["shares"] == 0
    assert abs(second.equity - 11000.0) < 1e-9


def test_snapshot_rejects_bad_price():
    p = Portfolio(10000)
    assert raises(ValueError, p.snapshot, D0, {"AAA": 0.0})


def test_equity_curve_returns_and_drawdown():
    p = Portfolio(100.0)
    for d, eq in zip(pd.date_range("2026-01-01", periods=4), [100.0, 120.0, 90.0, 110.0]):
        p.cash = eq
        p.snapshot(d, {})
    assert p.equity_curve() == [100.0, 120.0, 90.0, 110.0]
    assert abs(p.returns()[0] - 0.2) < 1e-9
    assert abs(p.max_drawdown() - (-0.25)) < 1e-9        # 120 -> 90
    assert p.final_equity() == 110.0


def test_empty_portfolio_helpers_do_not_crash():
    p = Portfolio(5000)
    assert p.equity_curve() == []
    assert p.returns() == []
    assert p.drawdowns() == []
    assert p.max_drawdown() == 0.0
    assert p.final_equity() == 5000


if __name__ == "__main__":
    sys.exit(1 if run_tests(globals(), "Portfolio") else 0)
