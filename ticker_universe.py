## This code gets lists of ticker symbols within one of three universes: S&P500, NASDAQ 100, and Dow 30. 
## Author: Miguel Opeña
## Version: 3.0.0

"""	SNP_500_LINK: the Wikipedia link to a table of the S&P 500 constituents
	DOW_30_LINK: the Wikipedia link to a table of the Dow 30 constituents
	DOW_30_LOCS: the location of the Dow 30 ticker table
	NASDAQ_100_LINK: the third-party link to a table of the NASDAQ 100 constituents
	BLACKLIST: Class A stock that should not be included in the ticker scrapers
"""
SNP_500_LINK = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
DOW_30_LINK = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
NASDAQ_100_LINK = 'https://www.stockmonitor.com/nasdaq-stocks/'
BLACKLIST = ['GOOGL', 'DISCA', 'NWSA', 'FOXA', 'UAA', 'LBTYA']

def obtain_parse_nasdaq(seed="^NDX"):
	""" Parses third-party website for the constituent stock tickers in the Nasdaq 100.
		Website is read as dataframe, requiring special parser compared to the Wikipedia ones.

		Inputs: a seed ticker to include in the output (default: "^NDX" for the Nasdaq 100)
		Outputs: a list of stock tickers at the given link
    """
	data = pd.read_html(NASDAQ_100_LINK)
	# First table on page
	table = data[0]
	# Ticker information is in the Company column of the table
	# This line is specialized to the website in NASDAQ_100_LINK
	tickers = table.Company[0:]
	allTickers = []
	# Plants a seed ticker if given
	if seed != None:
		allTickers.append(seed)
	# Sifts through ticker column and adds to list
	for tick in tickers: 
		if tick not in BLACKLIST: allTickers.append(tick)
	return allTickers

def obtain_parse_wiki(selection, seed=None):
	""" Parses Wikipedia for the constituent stock tickers in either the S&P 500 or the Dow 30.

		Inputs: selection between S&P 500 ("SNP500") or the Dow 30 ("DOW30", as well as seed ticker (example: "^GSPC")
		Outputs: a list of stock tickers at the given link
    """
    link = ""
    tableLocation = [0, 0]
    if selection == "SNP500":
    	link = SNP_500_LINK
    elif selection == "DOW30":
    	link = DOW_30_LINK
    	tableLocation = [1, 2]
    else:
    	raise ValueError('ticker_universe.py unable to recognize selection of ticker universe. Please try again with either \"SNP500\" or \"DOW30\".')
	data = pd.read_html(link)
	# First table on page
	table = data[tableLocation[0]]
	# Ticker information is first column of table, skipping the header info
	tickers = table[tableLocation[1]][1:]
	allTickers = []
	# Plants a seed ticker if given
	if seed != None:
		allTickers.append(seed)
	# Sifts through ticker column and adds to list
	for tick in tickers: 
		if tick not in BLACKLIST: allTickers.append(tick)
	return allTickers