## This code consolidates all the parsing of command prompts. 
## Author: Miguel Opeña
## Version: 1.3.3

import logging
import os

import io_support
import ticker_universe

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

logger.info("----------INITIALIZING NEW RUN OF %s----------", os.path.basename(__file__))

def get_generic_from_prompts(prompts, query, default="", req=True):
	"""	Parses command prompt for a selection of ticker universe (tickerverse).
		Inputs: command prompts, name of query in prompts, default value of query (if applicable), check if query is required (default: yes)
		Outputs: ticker universe and name
	"""
	if query not in prompts:
		if req:
			logger.error("Required prompt {} not found. Please try again.".format(query))
			return None
		else:
			logger.info("Prompt {0} not found, default value of {1} used.".format(query, default))
			return default
	else:
		return prompts[prompts.index(query) + 1]

def get_tickerverse_from_prompts(prompts, query="-tickerUniverse", folderpath=None):
	"""	Parses command prompt for a selection of ticker universe (tickerverse).
		Inputs: command prompts, name of query in prompts
		Outputs: ticker universe and name
	"""
	tickerverse = []
	name = ""
	if query not in prompts:
		logger.error("Required prompt {} not found. Please try again.".format(query))
		return None
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
	# Yields data on USD to XYZ forex tickers
	elif "FOREX" in prompts:
		tickerverse = ticker_universe.obtain_parse_forex()
		name = "FOREX"
	# Yields data on all tickers at a given filepath
	elif "CURRENT" in prompts:
		if not folderpath:
			logger.error("You chose `CURRENT` as a command-line option for ticker universe, but failed to provide a filepath for this folder. Please try again.")
			return None
		tickerverse = io_support.get_current_symbols(folderpath)
		name = "CURRENT SYMBOLS"
	# Yields data on user-provided tickers
	else:
		tickerverse = prompts[prompts.index(query) + 1].split(",")
		name = "CUSTOM"
	return tickerverse, name