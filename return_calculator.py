## This code computes a few basic metrics of returns and performance. 
## Author: Miguel Opeña
## Version: 3.0.0

def get_rolling_returns(price):
	"""	Computes the rolling return (return at each timepoint relative to start) of price. 
		Inputs: prices over a certain timespan
		Outputs: rolling return over the given timespan
	"""
	return [100 * (i - price[0]) / abs(price[0]) for i in price]

def overall_returns(prices):
	"""	Simply computes percent returns over the entire time period.
		Can be used to rank stocks (as a basic strategy).
		Inputs: prices over a certain timespan
		Outputs: return over the given timespan
	"""
	return 100 * (prices[-1] - prices[0]) / abs(prices[0])

def portfolio_valuation(portfolio, baseline):
	"""	Values the aforementioned portfolio in terms of CLOSING PRICE against a baseline. 
		Inputs: dataframe of portfolio price over time, dataframe of baseline price over time
		Outputs: the portfolio's initial value, final value, overall returns; the baseline's returns
	"""
	# Calculate start value, end value, and returns on portfolio
	initialValue = portfolio.close[0]
	finalValue = portfolio.close[-1]
	returns = overall_returns(portfolio.close)
	baseReturns = overall_returns(baseline.close)
	# Returns all four variables
	return initialValue, finalValue, returns, baseReturns