## This code computes a few basic metrics of returns. 
## Author: Miguel Opeña
## Version: 3.4.3

import logging
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rolling_returns(prices):
	"""	Computes the rolling return (return at each timepoint relative to start) of price. 
		Inputs: prices over a certain timespan (Series or list)
		Outputs: rolling return over the given timespan
	"""
	# If input is Series, output is Dataframe
	if isinstance(prices, pd.Series):
		return 100 * (prices - prices[0]) / abs(prices[0])
	# If input is list, output is list
	elif isinstance(prices, list):
		return [100 * (i - prices[0]) / abs(prices[0]) for i in prices]
	else:
		logger.error("Unsupported data type given as input to exponential_moving_average in technicals_calculator.py")

def overall_returns(prices):
	"""	Simply computes percent returns over the entire time period.
		Can be used to rank stocks (as a basic strategy).
		Inputs: prices over a certain timespan
		Outputs: return over the given timespan
	"""
	# If input is Series, output is Dataframe
	return 100 * (prices[-1] - prices[0]) / abs(prices[0])