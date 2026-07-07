import pandas as pd

from typing import tuple
from strategies.base import Strategy
from trade import Trade
from results import BacktestResults

class BacktestEngine:
	def __init__(self, initial_cash: float = 10000, commission: float = 0.0):
		self.initial_cash = initial_cash
		self.commission = commission
		
	def _simulate(self, signals: pd.DataFrame) -> tuple[list[Trade], float]:
		trades = []
		cash = self.initial_cash
		shares = 0
		
		for index, row in signals.iterrows():
			row_signal = row["Signal"]
			row_price = row["Close"]

			if row_signal == 1 and shares == 0:
				entry_date = index
				entry_price = row_price
				cash_after_fee = cash - self.commission
				
				shares = cash_after_fee / row_price
				cash = 0
				entry_shares = shares

			if row_signal == -1 and shares > 0:
				exit_date = index
				exit_price = row_price
				
				cash = (shares * row_price) - self.commission
				shares = 0

				cash_before = entry_shares * entry_price
				profit = cash - cash_before
				return_pct = (profit / cash_before) * 100

				holding_period = (exit_date - entry_date).days
				
				trades.append(Trade(
					entry_date = entry_date,
					exit_date = exit_date,
					entry_price = entry_price,
					exit_price = exit_price,
					shares = entry_shares,
					commission = self.commission,
					profit = profit,
					return_pct = return_pct,
					holding_period = holding_period
				))
				
				buy_flag = False
				sell_flag = False

		if shares > 0:
			exit_date = signals.iloc[-1]["Index"]
			exit_price = signals.iloc[-1]["Close"]
			
			cash = shares * exit_price - self.commission
			shares = 0

			cash_before = entry_shares * entry_price
			profit = cash - cash_before
			return_pct = (profit / cash_before) * 100

			holding_period = (exit_date - entry_date).days
			
			trades.append(Trade(
					entry_date = entry_date,
					exit_date = exit_date,
					entry_price = entry_price,
					exit_price = exit_price,
					shares = entry_shares,
					commission = self.commission,
					profit = profit,
					return_pct = return_pct,
					holding_period = holding_period
				))

		return trades, cash

	def _calculate_results(self, trades: list, cash: float) -> BacktestResults:
		trade_amount = len(trades)
		
		total_return = sum(trade.profit for trade in trades)
		average_return = (total_return / trade_amount if trade_amount else 0.0)
		
		wins = sum(trade.profit > 0 for trade in trades)
		losses = sum(trade.profit < 0 for trade in trades)

		largest_win = max(trade.profit for trade in trades, default=0.0)
		largest_loss = min(trade.profit for trade in trades, default=0.0)

		winning_trades = [
			trade
			for trade in trades
			if trade.profit >= 0
		]
		average_win = (sum(winning_trades) / len(winning_trades) if winning_trades else 0.0)

		losing_trades = [
			trade
			for trade in trades
			if trade.profit < 0
		]
		average_loss = (sum(losing_trades) / len(losing_trades) if losing_trades else 0.0)

		win_rate = (wins / trade_amount if trade_amount else 0.0)

		longest_holding = max(trade.holding_period for trade in trades, default=0.0)
		shortest_holding = min(trade.holding_period for trade in trades, default=0.0)
		average_holding = (sum(trade.holding_period) / trade_amount if trade_amount else 0.0)
		
		results = BacktestResults(
			initial_cash = self.initial_cash,
			final_cash = cash,
			total_return = total_return,
			average_return = average_return,
			trades = trade_amount,
			wins = wins,
			largest_win = largest_win,
			average_win = average_win,
			winning_trades = winning_trades,
			losses = losses,
			largest_loss = largest_loss,
			average_loss = average_loss,
			losing_trades = losing_trades,
			win_rate = win_rate,
			longest_holding = longest_holding,
			shortest_holding = shortest_holding,
			average_holding = average_holding
		)
		
		return results
	
	def run(self, strategy: Strategy, df: pd.DataFrame) -> BacktestResults:
		signals = strategy.generate_signals(df)
		trades, cash = self._simulate(signals)
		return self._calculate_results(trades, cash)
