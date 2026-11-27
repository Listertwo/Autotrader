from models.trade import Trade

@dataclass
class TradeStats:
	@classmethod
	def from_trades(cls, trades: list[Trade]) -> TradeStats:
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
			if trade.profit > 0
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

		winloss_ratio = (average_win / abs(average_loss) if average_loss else 0.0)

		longest_holding = max((trade.holding_period for trade in trades), default=0.0)
		shortest_holding = min((trade.holding_period for trade in trades), default=0.0)
		average_holding = (sum(trade.holding_period for trade in trades) / trade_amount if trade_amount else 0.0)

		gross_profit, gross_loss, profit_factor, profit_rating = cls.calculate_profit(trades)
		
		expectancy = (win_rate * average_win) + (loss_rate * average_loss)

		return cls(
			trades = trades,
			trade_count = trade_amount,
			total_return = total_return,
			average_return = average_return,
			wins = wins,
			losses = losses,
			win_rate = win_rate,
			largest_win = largest_win,
			largest_loss = largest_loss,
			average_win = average_win,
			average_loss = average_loss,
			winning_trades = winning_trades,
			losing_trades = losing_trades,
			winloss_ratio = winloss_ratio,
			gross_profit = gross_profit,
			gross_loss = gross_loss,
			profit_factor = profit_factor,
			profit_rating = profit_rating,
			expectancy = expectancy,
			longest_holding = longest_holding,
			shortest_holding = shortest_holding,
			average_holding = average_holding,
		)
	
	@staticmethod
	def calculate_profit(trades: list[Trade]) -> tuple[float, float, float, str]:
		gross_profit = sum(
			trade.profit
			for trade in trades
			if trade.profit > 0
		)

		gross_loss = abs(sum(
			trade.profit
			for trade in trades
			if trade.profit < 0
		))

		if not trades:
			return 0.0, 0.0, 0.0, "N/A"

		profit_factor = gross_profit / gross_loss if gross_loss else float("inf")

		if profit_factor >= 2:
			profit_rating = "Excellent"
		elif profit_factor >= 1:
			profit_rating = "Net Positive"
		else:
			profit_rating = "Losing"

		return gross_profit, gross_loss, profit_factor, profit_rating
		
	trades: list[Trade]
	trade_count: int
	total_return: float
	average_return: float
	wins: int
	losses: int
	win_rate: float
	largest_win: float
	largest_loss: float
	average_win: float
	average_loss: float
	winning_trades: list[Trade]
	losing_trades: list[Trade]
	winloss_ratio: float
	gross_profit: float
	gross_loss: float
	profit_factor: float
	profit_rating: str
	expectancy: float
	longest_holding: float
	shortest_holding: float
	average_holding: float
