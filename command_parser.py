## This code consolidates all the parsing of command prompts. 
## Author: Miguel Opeña
## Version: 1.2.1

from warnings import warn

import ticker_universe

def get_generic_from_prompts(prompts, query, default="", req=True):
	"""	Parses command prompt for a selection of ticker universe (tickerverse).
		Inputs: command prompts, name of query in prompts, default value of query (if applicable), check if query is required (default: yes)
		Outputs: ticker universe and name
	"""
	if query not in prompts:
		if req:
			message = "Required prompt {} not found. Please try again.".format(query)
			raise ValueError(message)
		else:
			message = "Prompt {0} not found, default value of {1} used.".format(query, default)
			warn(message, UserWarning)
			return default
	else:
		return prompts[prompts.index(query) + 1]

def get_tickerverse_from_prompts(prompts, query="-tickerUniverse"):
	"""	Parses command prompt for a selection of ticker universe (tickerverse).
		Inputs: command prompts, name of query in prompts
		Outputs: ticker universe and name
	"""
	tickerverse = []
	name = ""
	if query not in prompts:
		message = "Required prompt {} not found. Please try again.".format(query)
		raise ValueError(message)
	# Yields data on the S&P 500
	elif "SNP500" in prompts:
		tickerverse = ticker_universe.obtain_parse_wiki(selection="SNP500", seed="^GSPC")
		name = "SNP500"
	# Yields data on the Dow 30
	elif "DOW30" in prompts:
		tickerverse = ticker_universe.obtain_parse_wiki(selection="DOW30", seed="^DJI")
		name = "DOW30"
	# Yields data on the NASDAQ 100
	elif "NASDAQ100" in prompts:
		tickerverse = ticker_universe.obtain_parse_nasdaq()
		name = "NASDAQ100"
	# Yields data on the ETF100
	elif "ETF100" in prompts:
		tickerverse = ticker_universe.obtain_parse_etfs()
		name = "ETF100"
	elif "MF25" in prompts:
		tickerverse = ticker_universe.obtain_parse_mutual_funds()
		name = "MF25"
	# Yields data on user-provided tickers
	else:
		tickerverse = prompts[prompts.index(query) + 1].split(",")
		name = "CUSTOM"
	return tickerverse, name