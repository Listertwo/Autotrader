from data.downloader import get_data
from strategies.momentum import MacdStrategy
from backtest.engine import BacktestEngine

# ------------------------------------------------------------------ SETTINGS
SYMBOLS = ["AAPL", "NVDA", "MSFT"]
PERIOD = "1y"
INTERVAL = "1d"

INITIAL_CASH = 10000
COMMISSION = 0.0
# ---------------------------------------------------------------------------


def main():
	data = get_data(SYMBOLS, interval=INTERVAL, period=PERIOD)

	strategy = MacdStrategy()

	engine = BacktestEngine(initial_cash=INITIAL_CASH, commission=COMMISSION)

	results = engine.run(strategy, data)

	print(results)
	results.print_trades()


if __name__ == "__main__":
	main()
