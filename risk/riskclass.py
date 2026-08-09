class Risk:
	def __init__(self, annualize: bool = True, trading_periods: int = 252):
		self.annualize = annualize
		self.trading_periods = trading_periods

	def volatility(self, df: pd.DataFrame, date) -> float:



		col = "Returns_Close"

		if col not in df.columns:
			df = add_returns(df)

		returns = df.loc[df.index < date, col]
		vol = returns.std()

		if self.annualize:
			vol *= np.sqrt(self.trading_periods)

		return float(vol)
