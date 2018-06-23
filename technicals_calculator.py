## This code contains a bunch of code for technical indicators.
## Author: Miguel Opeña
## Version: 1.0.0

import pandas as pd

def SMA(inputValues, startDate, endDate, numPeriods=30):
	"""	Computes the simple moving average (SMA) of a time series over certain timespan.
		Inputs: input values, start and end date of window, number of periods in SMA
		Outputs: SMA over given timespan
	"""
	# Isolates the ticker data between the start date and end date
	dataWindow = inputValues[startDate:endDate]
	# Computes the rolling mean (default: 30-day and 90-day)
	sma = inputValues.rolling(numPeriods).mean()
	sma.columns = ['SMA' + str(numPeriods)]
	return sma
