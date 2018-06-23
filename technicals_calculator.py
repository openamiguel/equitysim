## This code contains a bunch of code for technical indicators.
## Author: Miguel Opeña
## Version: 1.1.0

import pandas as pd

def SMA(inputValues, numPeriods=30):
	"""	Computes the simple moving average (SMA) of a time series over certain timespan.
		Inputs: input values, number of periods in SMA
		Outputs: SMA over given timespan
	"""
	# Computes the rolling mean (default: 30-day and 90-day)
	sma = inputValues.rolling(numPeriods).mean()
	sma.columns = ['SMA' + str(numPeriods)]
	return sma