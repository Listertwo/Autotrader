from data.downloader import get_data
from strategies.trend import GoldenCrossStrategy
from backtest.engine import BacktestEngine

df = get_data("AAPL", period="5y", interval="1h")

strategy = GoldenCrossStrategy()

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()