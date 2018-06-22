## This code models a very basic mean reversion strategy, using daily closing prices of one stock. 
## Author: Miguel Opeña
## Version: 1.5.0

import pandas as pd
import numpy as np

# Turn this code into a trend/baseline calculator based on simple moving avg
def placeholder():
	# Reads file from given filepath (entails assumptions about file name)
	filePath = FILE_PATH.replace(KEYWORD, symbol)
	ticker = pd.read_csv(filePath, index_col='timestamp')
	# Isolates the ticker data between the start date and end date
	thisTime = ticker[startDate:endDate]
	time = thisTime.index
	# Closing data only!
	price = thisTime.close
	# Computes the rolling mean (default: 30-day and 90-day)
	roll01 = price.rolling(roll[0]).mean()
	roll02 = price.rolling(roll[1]).mean()
	# Compiles all the data together for export
	priceRollingData = pd.concat([price, roll01, roll02], axis=1, join='inner')
	priceRollingData.dropna(inplace=True)
	priceRollingData.columns = ['close', 'roll', 'rollTrend']

### WARNING: THIS STRATEGY IS BOGUS. IT MAY NOT EVEN MODEL WHAT I INTENDED IT TO. 
def meanReversionStrategy(priceRollingData, startingValue=1000, numBuys=1):
	price = priceRollingData.close.values.tolist()
	roll = priceRollingData.roll.values.tolist()
	rollTrend = priceRollingData.rollTrend.values.tolist()

	numPositions = 0
	portfolio = startingValue
	isGreater = roll[0] > rollTrend[0]

	for i in range(len(price)):
		thisPrice = price[i]
		thisRoll = roll[i]
		thisRollTrend = rollTrend[i]
		# print("Current portfolio value: %d" % portfolio)
		# print("Number of positions held: %d" % numPositions)
		# Go long
		if thisRoll < thisRollTrend and isGreater:
			isGreater = not isGreater
			# Dump previous short positions
			portfolio += numPositions * thisPrice
			print("Dumped %d positions. " % numPositions)
			numPositions = 0
			# Build up long positions
			portfolio -= numBuys * thisPrice
			numPositions += numBuys
			print("Acquired %d LONG positions.\n" % numBuys)
		# Go short
		elif thisRoll > thisRollTrend and not isGreater:
			isGreater = not isGreater
			# Dump previous long positions
			portfolio += numPositions * thisPrice
			print("Dumped %d positions. " % numPositions)
			numPositions = 0
			# Build up short positions
			portfolio += numBuys * thisPrice
			numPositions -= numBuys
			print("Acquired %d SHORT positions.\n" % numBuys)
		# Otherwise, simply hold one's position
	return portfolio

def meanReversionStrategyZScore(priceRollingData, startingValue=1000, numBuys=1):
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
priceRollingData = meanReversionPlot("TSLA", "Tesla", startDate, endDate, roll=[1,90])
startingValue = 1000000
numBuys = 300
endingValue = meanReversionStrategyZScore(priceRollingData, startingValue=startingValue, numBuys=numBuys)
print("Profit (percent): %f" % (100 * (endingValue - startingValue) / startingValue))