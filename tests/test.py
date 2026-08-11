from data.downloader import get_data
from strategies.momentum import MacdStrategy
from backtest.engine import BacktestEngine

df = get_data("^GSPC", period="1mo", interval="5m")

strategy = MacdStrategy()

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()