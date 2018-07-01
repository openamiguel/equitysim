## This code computes a few basic metrics of returns. 
## Author: Miguel Opeña
## Version: 3.4.0

import numpy as np
import pandas as pd

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