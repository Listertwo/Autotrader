from data.downloader import get_data
from strategies.momentum import MacdStrategy
from backtest.engine import BacktestEngine

symbols = ["AAPL", "NVDA", "MSFT"]

df = get_data(symbols, interval="1d", period="1y")

strategy = MacdStrategy()

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()