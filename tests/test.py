from data.downloader import get_data
from strategies import Strategy
from backtesting.engine import BacktestEngine

symbols = ["AAPL", "NVDA", "MSFT"]

df = get_data(symbols, interval="1d", period="1y")

strategy = GoldenCrossStrategy()

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()
