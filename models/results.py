from __future__ import annotations

import pandas as pd

from dataclasses import dataclass

from models.trade import Trade
from backtest.portfolio import Portfolio

@dataclass
class BacktestResults:
	@classmethod
	def from_portfolio(cls, portfolio: Portfolio) -> BacktestResults:
		trades = portfolio.trades
		cash = portfolio.cash
		returns = pd.Series(portfolio.returns())

		grouped: dict[str, list[Trade]] = {}
		for trade in portfolio.trades:
			grouped.setdefault(trade.strategy, []).append(trade)
		
		sharpe_ratio, sharpe_rating = cls.calculate_sharpe(returns)
		
		return cls(
			initial_cash = portfolio.initial_cash,
			final_cash = cash,
			stats = TradeStats.from_trades(portfolio.trades),
			by_strategy = {label: TradeStats.from_trades(trades) for label, trades in grouped.items()},
			cagr = cls.calculate_cagr(portfolio),
			volatility = cls.calculate_volatility(returns),
			sharpe_ratio = sharpe_ratio,
			sharpe_rating = sharpe_rating,
			sortino_ratio = cls.calculate_sortino(returns),
			drawdown = portfolio.drawdowns(),
			max_drawdown = portfolio.max_drawdown(),
			calmar_ratio = cls.calculate_calmar(portfolio),
			exposure = cls.calculate_exposure(portfolio),
			recovery = cls.calculate_recovery(portfolio)
		)

	@staticmethod
	def calculate_cagr(portfolio: Portfolio) -> float:
		if len(portfolio.history) < 2 or portfolio.initial_cash <= 0:
			return 0.0

		first_date = portfolio.history[0].date
		last_date = portfolio.history[-1].date
		years = (last_date - first_date).days / 365.25

		if years <= 0:
			return 0.0
		
		return (portfolio.final_equity() / portfolio.initial_cash) ** (1/years) - 1

	@staticmethod
	def calculate_volatility(returns: pd.Series) -> float:
		if len(returns) < 2:
			return 0.0

		std = returns.std()

		return 0.0 if pd.isna(std) else std * (252 ** 0.5)

	@staticmethod
	def calculate_sharpe(returns: pd.Series) -> tuple[float, str]:
		sqrt252 = 252 ** 0.5
		
		if len(returns) < 2 or pd.isna(returns.std()) or returns.std() == 0:
			return 0.0, "N/A"

		ratio = sqrt252 * returns.mean() / (returns.std())

		if ratio < 1:
			rating = "Mediocre"
		elif ratio < 2:
			rating = "Good"
		elif ratio < 3:
			rating = "Excellent"
		else:
			rating = "Exceptional"
		
		return ratio, rating

	@staticmethod
	def calculate_sortino(returns: pd.Series) -> float:
		sqrt252 = 252 ** 0.5

		if len(returns) < 2:
			return 0.0

		downside_deviation = (returns.clip(upper=0) ** 2).mean() ** 0.5

		if downside_deviation == 0:
			return 0.0

		return sqrt252 * (returns.mean() / downside_deviation)

	@staticmethod
	def calculate_calmar(portfolio: Portfolio) -> float:
		cagr = BacktestResults.calculate_cagr(portfolio)

		max_drawdown = abs(portfolio.max_drawdown())

		if max_drawdown == 0:
			return 0.0

		return cagr / max_drawdown

	@staticmethod
	def calculate_exposure(portfolio: Portfolio) -> float:
		"""Average share of equity invested in positions across all snapshots."""
		if not portfolio.history:
			return 0.0

		deployed = [
			snapshot.market_value / snapshot.equity
			for snapshot in portfolio.history
			if snapshot.equity > 0
		]

		return sum(deployed) / len(deployed) if deployed else 0.0

	@staticmethod
	def calculate_recovery(portfolio: Portfolio) -> float:
		max_drawdown = abs(portfolio.max_drawdown())

		if max_drawdown == 0 or portfolio.initial_cash <= 0:
			return 0.0

		net_return = portfolio.final_equity() / portfolio.initial_cash - 1

		return net_return / max_drawdown

	def __str__(self) -> str:
		s = self.stats
		
		return (
			f"\n"
			f"{'=' * 60}\n"
			f"BACKTEST RESULTS\n"
			f"{'=' * 60}\n"
			f"Initial Cash:      ${self.initial_cash:,.2f}\n"
			f"Final Cash:        ${self.final_cash:,.2f}\n"
			f"Net Profit:        ${s.total_return:,.2f}\n"
			f"Average Trade:     ${s.average_return:,.2f}\n"
			f"\n"
			f"Trades:            {s.trade_count}\n"
			f"Wins:              {s.wins}\n"
			f"Losses:            {s.losses}\n"
			f"Win Rate:          {s.win_rate:.2%}\n"
			f"\n"
			f"Largest Win:       ${s.largest_win:,.2f}\n"
			f"Largest Loss:      ${s.largest_loss:,.2f}\n"
			f"Average Win:       ${s.average_win:,.2f}\n"
			f"Average Loss:      ${s.average_loss:,.2f}\n"
			f"\n"
			f"Profit Factor:     {s.profit_factor:.2f}, {s.profit_rating}\n"
			f"Sharpe Ratio:      {self.sharpe_ratio:.2f}, {self.sharpe_rating}\n"
			f"Sortino Ratio:     {self.sortino_ratio:.2f}\n"
			f"Calmar Ratio:      {self.calmar_ratio:.2f}\n"
			f"\n"
			f"CAGR:              {self.cagr:.2%}\n"
			f"Volatility:        {self.volatility:.2%}\n"
			f"Max Drawdown:      {self.max_drawdown:.2%}\n"
			f"Exposure:          {self.exposure:.2%}\n"
			f"Recovery Factor:   {self.recovery:.2f}\n"
			f"{'=' * 60}\n"
			f"BY STRATEGY\n"
			f"{self.strategy_table()}\n"
			f"{'=' * 60}"
		)

	def strategy_table(self) -> str:
		header = f"{'Strategy':<32}{'Trades':>7}{'Win %':>8}{'Net P&L':>13}{'PF':>7}{'Expect.':>10}"
		rows = [header, "-" * len(header)]
		for label, s in self.by_strategy.items():
			rows.append(f"{label:<32}{s.trade_count:>7}{s.win_rate:>8.1%}{s.total_return:>13,.2f}{s.profit_factor:>7.2f}{s.expectancy:10,.2f}")
		return "\n".join(rows)
	
	def print_trades(self):
		print("\nTrades")
		print("=" * 60)

		for trade in self.stats.trades:
			print(trade)
	
	initial_cash: float
	final_cash: float

	stats: TradeStats
	by_strategy: dict[str, TradeStats]

	cagr: float

	volatility: float

	sharpe_ratio: float
	sharpe_rating: str

	sortino_ratio: float

	drawdown: float
	max_drawdown: float

	calmar_ratio: float

	exposure: float

	recovery: float
