from data.downloader import get_data
from strategies.momentum import RsiStrategy
from backtest.engine import BacktestEngine

df = get_data("AAPL", period="1y", interval="1h")

strategy = RsiStrategy()

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()