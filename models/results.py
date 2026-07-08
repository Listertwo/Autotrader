from dataclasses import dataclass
from __future__ import annotations
from trade import Trade

@dataclass
class BacktestResults:
	@classmethod
	def from_portfolio(cls, portfolio: Portfolio) -> BacktestResults:
		trades = portfolio.trades
		cash = portfolio.cash

		trade_amount = len(trades)
		
		total_return = sum(trade.profit for trade in trades)
		average_return = (total_return / trade_amount if trade_amount else 0.0)
		
		wins = sum(trade.profit > 0 for trade in trades)
		losses = sum(trade.profit < 0 for trade in trades)

		largest_win = max((trade.profit for trade in trades), default=0.0)
		largest_loss = min((trade.profit for trade in trades), default=0.0)

		winning_trades = [
			trade
			for trade in trades
			if trade.profit >= 0
		]
		average_win = (sum(trade.profit for trade in winning_trades) / len(winning_trades) if winning_trades else 0.0)

		losing_trades = [
			trade
			for trade in trades
			if trade.profit < 0
		]
		average_loss = (sum(trade.profit for trade in losing_trades) / len(losing_trades) if losing_trades else 0.0)

		win_rate = (wins / trade_amount if trade_amount else 0.0)
		loss_rate = (losses / trade_amount if trade_amount else 0.0)

		longest_holding = max((trade.holding_period for trade in trades), default=0.0)
		shortest_holding = min((trade.holding_period for trade in trades), default=0.0)
		average_holding = (sum(trade.holding_period for trade in trades) / trade_amount if trade_amount else 0.0)

		returns = pd.Series(portfolio.returns())

		sharpe_ratio, sharpe_rating = cls.calculate_sharpe(returns)
		
		gross_profit, gross_loss, profit_factor, profit_rating = cls.calculate_profit(trades)

		expectancy = (win_rate * average_win) - (loss_rate * average_loss)
		
		return cls(
			initial_cash = portfolio.initial_cash,
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
			average_holding = average_holding,
			cagr = cls.calculate_cagr(portfolio),
			volitility = cls.calculate_volitility(returns),
			sharpe_ratio = sharpe_ratio,
			sharpe_rating = sharpe_rating,
			sortino_ratio = cls.calculate_sortino(returns),
			drawdown = portfolio.drawdown(),
			max_drawdown = portfolio.max_drawdown(),
			calmar_ratio = cls.calculate_calmar(portfolio),
			gross_profit = gross_profit,
			gross_loss = gross_loss,
			profit_factor = profit_factor,
			profit_rating = profit_rating,
			expectancy = expectancy,
			exposure = cls.calculate_exposure(trades),
			recovery = cls.calculate_recovery()
		)

	def calculate_cagr(cls, portfolio: Portfolio) -> float:
		first_date = portfolio.history[0].date
		last_date = portfolio.history[-1].date
		years = (last_date - first_date).days / 365.25

		return (portfolio.cash / portfolio.initial_cash) ** (1/years) - 1

	def calculate_volitility(cls, returns: pd.Series) -> float:
		return returns.std()

	def calculate_sharpe(cls, returns: pd.Series) -> tuple[float, str]:
		ratio = (returns.mean() / returns.std())

		if ratio < 1:
			rating = "Mediocre"
		elif ratio > 1 and ratio < 2:
			rating = "Good"
		elif ratio > 2 and ratio < 3:
			rating = "Excellent"
		elif ratio > 3:
			rating = "Exceptional"
		
		return ratio, rating

	def calculate_sortino(cls, returns: pd.Series) -> float:
		downside = returns[returns < 0]

		return (returns.mean() / downside.std())

	def calculate_calgar(cls, portfolio: Portfolio) -> float:
		cagr = cls.calculate_cagr(portfolio)

		return cagr / abs(portfolio.max_drawdown())

	def calculate_profit(cls, trades: list[Trade]) -> tuple[float, float, float, str]:
		gross_profit = sum(
			trade.profit
			for trade in trades
			if trade.profit > 0
		)

		gross_loss = sum(
			trade.profit
			for trade in trades
			if trade.profit < 0
		)

		profit_factor = gross_profit / gross_loss

		if profit_factor > 1:
			profit_rating = "Net Positive"
		elif profit_factor > 2:
			profit_rating = "Excellent"
		else:
			profit_rating = "Nothing Gained"

		return gross_profit, gross_loss, profit_factor, profit_rating

	def calculate_exposure(cls, trades: list[Trade]) -> float:
		days_in_market = sum(
			trade.holding_period
			for trade in trades
		)

		return days_in_market / 365 #Later implement total market day tally, possibly stored in Portfolio?

	
		
	
	initial_cash: float
	final_cash: float

	total_return: float
	average_return: float

	trades: int

	wins: int
	largest_win: float
	average_win: float
	winning_trades: list[Trade]
	
	losses: int
	largest_loss: float
	average_loss: float
	losing_trades: list[Trade]

	win_rate: float
	winloss_ratio: float

	longest_holding: int
	shortest_holding: int
	average_holding: float

	cagr: float

	volatility: float

	sharpe_ratio: float
	sharpe_rating: str

	sortino_ratio: float

	drawdown: float
	max_drawdown: float

	calmar_ratio: float

	gross_profit: float
	gross_loss: float
	profit_factor: float
	profit_rating: str

	expectancy: float

	exposure: float

	recovery: float
