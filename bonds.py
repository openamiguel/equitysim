## This code uses basic numerical inputs to model basic bonds over time.
## Rule: the only possible inputs are those known at the initial transaction. 
## Author: Miguel Opeña
## Version: 1.1.0

import logging
from math import exp
import numpy as np

LOGDIR = "/Users/openamiguel/Desktop/LOG"
# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Set file path for logger
handler = logging.FileHandler('{}/equitysim.log'.format(LOGDIR))
handler.setLevel(logging.DEBUG)
# Format the logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Add the new format
logger.addHandler(handler)
# Format the console logger
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)
# Add the new format to the logger file
logger.addHandler(consoleHandler)

# Initializes frequencies for bond calculations
ANNUM = 1.0
SEMI_ANNUM = 2.0
QUARTERLY = 4.0
MONTHLY = 12.0

def periodic_compound(interest, freq, current_time):
	""" Periodic compounding function.
		Inputs: interest rate, frequency of payoff, current time
		Outputs: compounding factor for given cash flow at specified time
	"""
	return (1 + interest / freq) ** (-freq * current_time)

def continuous_compound(interest, freq, current_time):
	""" Continuous (exponential) compounding function.
		Inputs: interest rate, frequency of payoff, current time
		Outputs: compounding factor for given cash flow at specified time
	"""
	return exp(-interest * current_time)

def fixed_rate_bond(par, coupon, interest, maturity=5, freq=1.0, compound_function=periodic_compound):
	""" Computes the initial price of a fixed-rate bond (including zero compound).
		Inputs: par value, coupon value, interest rate, maturity (in years), 
			frequency of samples (in Hertz), choice of compound function (default: periodic)
		Outputs: fair initial price of bond
	"""
	# Handle case of zero-coupon bond
	if coupon == 0:
		payoff = par * ((1 + interest / freq) ** (-freq * maturity))
		return payoff
	# Otherwise, price the bond as normal
	initialprice = par
	logger.debug("Par value of bond: $%.2f", initialprice)
	payoff = 0
	# Increments through each coupon payment
	for time in np.arange(1.0, maturity + 1.0 / freq, 1.0 / freq):
		increment = coupon * compound_function(interest, freq, time)
		payoff += increment
		logger.debug("Increment at year %.2f: $%.2f", time, increment)
	# Adds final payoff of par value
	payoff += par * compound_function(interest, freq, maturity)
	return payoff	 

print(fixed_rate_bond(1000, 40, 0.04, maturity=4))