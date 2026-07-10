from data.downloader import get_data
from strategies import Strategy
from backtesting.engine import BacktestEngine

df = get_data("AAPL")

strategy = GoldenCrossStrategy()

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()
