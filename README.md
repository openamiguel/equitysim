# equitysim

This code harnesses the AlphaVantage API to download and analyze equity data on any constituent of the following groups: 
- the S&P 500 stock index
- the Dow 30 stock index
- the NASDAQ 100 stock index
- the top 100 most-traded ETFs
- the top 25 most-traded mutual funds
- numerous forex tickers, converting from US dollar to another currency 
These data are readily transformed using technical indicators and processed into features for machine learning. 

This code also downloads and analyzes data from the [United States SEC's Financial Statements datasets](https://www.sec.gov/dera/data/financial-statement-data-sets.html), which supplies additional feature data from a fundamental analysis standpoint. 

## AlphaVantage data download/update
- **download.py**
  - class `CDownloader` downloads and processes symbols from AlphaVantage API into local drive
    - `load_single` handles one symbol
    - `load_separate` handles many symbols at once
  - class `CLoader` downloads and processes symbols from local drive into variables
    - `load_single_drive` handles one symbol
    - `load_combined_drive` handles many symbols at once
  - class `CMacroDownloader` downloads and processes data from varying macro data sources
    - `yield_curve_year` gets yield curve data for one year (source: data.treasury.gov)
    - `yield_curve_multi` gets yield curve data for many years
  - command prompt options:
    - `-tickerUniverse`: collection of tickers to download (can also be a CSV of ticker symbols) 
    - `-folderPath`: location of folder to store file
    - `-apiKey`: AlphaVantage API key (user-specific)
    - `-function`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
- **auto_update.py**
  - class `CUpdater` updates all files at a given folder position
    - `get_downloader_object` builds a downloader object to load the data
    - `update_files` performs the update in full
  - command prompt options:
    - `-folderPath`: location of folder to look for files
    - `-apiKey`: AlphaVantage API key (user-specific)
- See [the AlphaVantage documentation](https://www.alphavantage.co/documentation/) for more details on their API calls. 

## fundamental analysis
- **fundamental_load.py**
  - `edgar_extract` downloads and unzips data directly from the SEC website
  - `proc_in_directory` walks through download directory and parses each file
  - `edgar_load` performs post-processing on files, which makes them smaller
  - command prompt options:
    - `-folderPath`: location of folder to download data
    - `-stockFolderPath`: location of folder to look for stock data
    - `-financialFolderPath`: location of folder to load financial data
    - `-suppressDownload`: order to suppress downloading data (i.e. already downloaded)
    - `-suppressProcess`: order to suppress processing data (i.e. already processed)
- **fundamental_pull.py**
  - `get_tags_in_file` returns list of unique tags in a single company's JSON file
  - `get_tag_data` writes data on one chosen tag to an output file
  - command prompt options:
    - pending
- **fundamental_support.py**
  - `get_sic_names` scrapes SEC.gov for data on industry codes (SICs)
  - `edgar_sub` parses submission files
  - `edgar_num` parses number files
  - `edgar_pre` parses presentation files
  - `edgar_tag` parses tag files
  - command prompt options:
    - *none* (does not need any)
- **return_calculator.py**
  - `get_rolling_returns` calculates a list of rolling returns on an asset or portfolio
  - `overall_returns` calculates the overall return from start to finish
  - command prompt options:
    - *none* (does not need any)

## technical analysis
- **technicals.py**
  - see the code for additional descriptions (there are too many functions to list here)

## machine learning suite
- **stats.py**
  - `adf` computes the augmented Dickey-Fuller test for mean reversion properties
  - command prompt options: 
    - none (for now!)
- **feature_build.py**
  - `get_features` returns a dataframe of features, with one column for each indicator listed above
  - command prompt options:
    - `-tickerUniverse`: collection of tickers to download (can also be a comma-delimited list of ticker symbols) 
    - `-baseline`: selection of symbol to use as baseline asset/index
    - `-startDate`: start date of data to process into features
    - `-endDate`: end date of aforementioned
    - `-function`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
    - `-folderPath`: location of folder to write the files
    - `-plotOnly`: if indicated, plot the heatmaps; otherwise, build from scratch without plots

## general simulators
- **strategy.py**
  - `hold_clear` builds a simple strategy for buying/selling, holding one's position, and clearing
  - `crossover` builds a strategy for buying when trend crosses below baseline and selling when trend crosses above (or vice versa)
  - `zscore_distance` builds a strategy for for buying when trend crosses far below baseline and selling when trend crosses far above (or vice versa), as measured by z-scores
  - command prompt options:
    - *none* (does not need any)
- **portfolio.py**
  - `asset_ranker` ranks a group of assets based on a certain criterion, choosing which ones should be bought long or sold short
  - `apply_trades` applies any series of trades to any set of symbols, yielding a portfolio simulation
  - command prompt options:
    - *none* (does not need any)
- **performance.py**
  - `beta` calculates asset/portfolio beta
  - `sharpe_ratio` calculates the Sharpe ratio for a given portfolio
    - proxy for risk-free rate is the 3-month US T-bill
  - `treynor_ratio` calculates the Treynor ratio for given portfolio
    - proxy for risk-free rate is the 3-month US T-bill
  - `returns_valuation` values the portfolio (initial value, final value, and return) against a benchmark (such as an index)
  - command prompt options:
    - *none* (does not need any)

## miscellaneous
- **arxiv.py**
  - class `CArxivParser` parses all papers in a given sub-category of Arxiv papers
    - `get_feed` gets a feed object that represents the paper data
    - `get_total_results` gets the number of results in given sub-category
    - `parse_feed` parses the feed object for a particular set of data
  - class `CArxivParserMulti` parses all papers across many sub-categories of Arxiv papers
    - `parse_all` instantiates class `CArxivParser` for each sub-category
- **command_parser.py**
  - class `CCmdParser` parses a list of command prompts
    - `get_generic` gets any non-tickerverse prompt from prompts
    - `get_tickerverse` returns a tickerverse and its name from prompts
  - command prompt options:
    - *none* (does not need any)
- **io_support.py**
  - `get_current_symbols` looks for stock ticker symbols in the files within directory
  - `memory_check` verifies if file occupies too much space in RAM
  - `merge_chunked` inner-joins a small dataframe (left) with a large one (right), the latter being read in chunks
  - `write_as_append` writes dataframe to file path in append mode
  - command prompt options:
    - *none* (does not need any)
- **bonds.py**
  - `periodic_compound` calculates the bond discounting factor under periodic compounding
  - `continuous_compound` calculates the bond discounting factor under continuous compounding
  - `fixed_rate_bond` calculates the initial bond price for zero- and non-zero-coupon fixed-rate bonds
- **ticker_universe.py**
  - `obtain_parse_nasdaq` gets the Nasdaq 100 stocks from stockmonitor.com. 
  - `obtain_parse_wiki` gets either the S&P 500 or the Dow 30 stocks from Wikipedia. 
  - `obtain_parse_mutual_funds` gets the top 25 mutual funds from marketwatch.com.
  - `obtain_parse_etfs` gets the top 100 ETFs from etfdb.com.
  - command prompt options:
    - *none* (does not need any)
- **plotter.py**
  - `feature_plot` plots a file of features as a correlation heatmap
  - `candle_plot` plots a single asset in candlestick form
  - `price_plot` plots a single asset against any number of prices, trends, indicators, etc.
  - command prompt options:
    - `-symbol`: symbol of the asset to plot
    - `-folderPath`: location of folder to look for files
    - `-function`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
    - `-startDate`: start date of data to plot
    - `-endDate`: end date of aforementioned
    - `-column`: choice of price or volume to plot
    - `-candlestick`: choice to use candlestick plot instead of typical plot
