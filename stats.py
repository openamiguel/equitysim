#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Code for the augmented Dickey-Fuller mean reversion test. 
## Source: https://www.quantstart.com/articles/Basics-of-Statistical-Mean-Reversion-Testing
## Author: Miguel Opeña
## Version: 1.0.0

import logging
# Import the time series library
import statsmodels.tsa.stattools as ts

import download as dl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def adf(tick_data, column='close', lag_order=1, verbose=False):
	""" Computes the augmented Dickey-Fuller mean reversion test.
		Technically, determines whether process is Ornstein-Uhlenbeck or not.
		Inputs: OHLC data, choice of column, lag order, verbose logger output
		Outputs: results of the test
	"""
	adf = ts.adfuller(tick_data[column], lag_order)
	if verbose: 
		logger.info("Test Statistic: %.4f", adf[0])
		logger.info("P-value: %.4f", adf[1])
		logger.info("Number of lags: %d", adf[2])
		logger.info("Number of samples: %d", adf[3])
		for num in [1, 5, 10]:
			logger.info("Confidence interval %d%%: %.4f", num, adf[4][str(num) + "%"])
			outstr = " SATISFIED" if adf[0] < adf[4][str(num) + "%"] else " NOT satisfied"
			logger.info("Confidence interval %d%%: %s", num, outstr)
		logger.info("Max information criterion: %.4f", adf[5])
	return adf

def main():
	symbol = "AAPL"
	start_date = "2018-01-01"
	end_date = "2018-02-01"
	folderpath = "/Users/openamiguel/Documents/EQUITIES/stockDaily"
	tick_data = dl.load_single_drive(symbol, folderpath=folderpath)
	tick_data = tick_data[start_date:end_date]
	print(adf(tick_data, column='close', verbose=True))
	
if __name__ == "__main__":
	main()