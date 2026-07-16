from data.downloader import get_data
from strategies.crossover import EmaCrossoverStrategy
from backtest.engine import BacktestEngine

df = get_data("NFLX", period="1y", interval="1h")

strategy = EmaCrossoverStrategy(50, 200)

engine = BacktestEngine()

results = engine.run(strategy, df)

print(results)
results.print_trades()