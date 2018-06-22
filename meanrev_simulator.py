## This code models a very basic mean reversion strategy, using daily closing prices of one stock. 
## Author: Miguel Opeña
## Version: 1.5.0

import pandas as pd
import numpy as np

import technicals_indicator

# Later on: add option to switch buy/sell signals
def crossover(price_with_trends, startDate, endDate, numTrades=1):
	"""	Simulates a crossover strategy for a trend and baseline. 
		Sells if trend crosses down below baseline, buys if trend crosses up above baseline. 
		Inputs: price data with trend and baseline, start date for price window, end date for price window,  
			the lower quantile, the upper quantile, 
			order to switch long and short positions (default: no)
		Outputs: list of symbols to buy long and sell short
	"""
	# Sets up the price, trend, and baseline as lists (for ease of use)
	price = price_with_trends.price.values.tolist()
	trend = price_with_trends.trend.values.tolist()
	baseline = price_with_trends.baseline.values.tolist()
	# Initialize portfolio with zero positions
	numPositions = 0
	portfolio = startingValue
	# Initialize boolean check variable
	isGreater = trend[0] > baseline[0]
	# Start iterating through the price, trend, and baseline data
	for i in range(len(price)):
		thisPrice = price[i]
		thisRoll = trend[i]
		thisRollTrend = baseline[i]
		print("Current portfolio value: %d" % portfolio)
		print("Number of positions held: %d" % numPositions)
		# Go long
		if thisRoll < thisRollTrend and isGreater:
			isGreater = not isGreater
			# Dump previous short positions
			portfolio += numPositions * thisPrice
			print("Dumped %d positions. " % numPositions)
			numPositions = 0
			# Build up long positions
			portfolio -= numTrades * thisPrice
			numPositions += numTrades
			print("Acquired %d LONG positions.\n" % numTrades)
		# Go short
		elif thisRoll > thisRollTrend and not isGreater:
			isGreater = not isGreater
			# Dump previous long positions
			portfolio += numPositions * thisPrice
			print("Dumped %d positions. " % numPositions)
			numPositions = 0
			# Build up short positions
			portfolio += numTrades * thisPrice
			numPositions -= numTrades
			print("Acquired %d SHORT positions.\n" % numTrades)
		# Otherwise, simply hold one's position
		else: print("Positions held.\n")
	return portfolio

def zscore_distance(priceRollingData, startingValue=1000, numBuys=1):
	price = priceRollingData.close.values.tolist()
	roll = priceRollingData.roll.values.tolist()
	rollTrend = priceRollingData.rollTrend.values.tolist()
	stdev = np.std(roll)
	zscores = [(roll[i] - rollTrend[i]) / stdev for i in range(len(price))]

	numPositions = 0
	portfolio = startingValue

	for i in range(len(price)):
		thisPrice = price[i]
		thisZ = zscores[i]
		if numBuys * thisPrice >= portfolio:
			print("It seems you have run out of funds.")
			break
		# Sell short if z-score > 1
		if thisZ > 1:
			portfolio += thisPrice * numBuys
			numPositions -= numBuys
			print("Acquired %d SHORT positions.\n" % numBuys)
		# Buy long if z-score < -1
		elif thisZ < -1: 
			portfolio -= thisPrice * numBuys
			numPositions += numBuys
			print("Acquired %d LONG positions.\n" % numBuys)
		# Clear positions if z-score is too low
		elif abs(thisZ) < 0.5:
			portfolio += thisPrice * numPositions
			# Useless to display dumping 0 positions
			if numPositions > 0:
				print("Dumped %d positions. " % numPositions)
			numPositions = 0

	return portfolio

startDate = "2014-01-01"
endDate = "2018-06-01"
# To compare the stock itself with a moving average, set roll=[1, X]
priceRollingData = crossover("TSLA", "Tesla", startDate, endDate, roll=[1,90])
startingValue = 1000000
numBuys = 300
endingValue = zscore_distance(priceRollingData, startingValue=startingValue, numBuys=numBuys)
print("Profit (percent): %f" % (100 * (endingValue - startingValue) / startingValue))

technicals_indicator.SMA(price, startDate, endDate, numPeriods=30)