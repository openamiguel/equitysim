# equitysim

Harnesses the AlphaVantage API to pull, store, plot, and analyze equity data on the big players: any member of the S&P 500, Dow 30, or NASDAQ 100 indices, as well as any of the 100 most-traded ETFs and the top 25 most-traded mutual funds. 

Also downloads data from the US SEC's Financial Statements datasets, which can bring plenty of fundamental data into one's analysis. Data downloaded from ZIP files at this URL: [SEC EDGAR Financial Statement Datasets](https://www.sec.gov/dera/data/financial-statement-data-sets.html). 

See [the AlphaVantage documentation](https://www.alphavantage.co/documentation/) for more details on how API calls work within this code! 

## documentation of each file and its functions

### AlphaVantage data download/update suite
- **download.py**
  - `load_single` downloads and processes a single symbol from AlphaVantage API into a file
  - `load_single_drive` downloads and processes a single symbol from local drive into a variable
  - `load_separate` downloads and processes many symbols from AlphaVantage API into many files
  - `load_combined_drive` downloads and processes many symbols from local drive into one variable
  - command prompt options:
    - `-tickerUniverse`: collection of tickers to download (can also be a CSV of ticker symbols) 
    - `-folderPath`: location of folder to store file
    - `-apiKey`: AlphaVantage API key (user-specific)
    - `-function`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
- **auto_update.py**
  - `update_in_folder` updates all equity files in a folder, using the latest data from AlphaVantage
    - `-folderPath`: location of folder to look for files
    - `-apiKey`: AlphaVantage API key (user-specific)

### SEC EDGAR data download/update suite
- **edgar_load.py**
  - `download_unzip` downloads and unzips data directly from the SEC website
  - `proc_in_directory` walks through download directory and parses each file
  - `post_proc` performs post-processing on files, which makes them smaller
  - `json_build` builds one JSON file for each company chosen
- **edgar_parse.py**
  - `json_parse` provides backup parsing code to clean up the JSON files in edgar_load.py
  - `get_sic_names` scrapes SEC.gov for data on industry codes (SICs)
  - `submission_parse` parses submission files
  - `number_parse` parses number files
  - `presentation_parse` parses presentation files
  - `tag_parse` parses tag files

### simulator suite
- **strategy.py**
  - `hold_clear` builds a simple strategy for buying/selling, holding one's position, and clearing
  - `crossover` builds a strategy for buying when trend crosses below baseline and selling when trend crosses above (or vice versa)
  - `zscore_distance` builds a strategy for for buying when trend crosses far below baseline and selling when trend crosses far above (or vice versa), as measured by z-scores
- **portfolio.py**
  - `asset_ranker` ranks a group of assets based on a certain criterion, choosing which ones should be bought long or sold short
  - `apply_trades` applies any series of trades to any set of symbols, yielding a portfolio simulation
- **performance.py**
  - `sharpe_ratio` calculates the Sharpe ratio for a given portfolio
    - proxy for risk-free rate is the 3-month US T-bill
  - `returns_portfolio` values the portfolio (initial value, final value, and return) against a benchmark (such as an index)
  - command prompt options:
    - *none* (does not need any)

### assorted calculators and misc. programs
- **command_parser.py**
  - `get_generic_from_prompts` gets any non-tickerverse prompt from a list of command prompts
  - `get_tickerverse_from prompts` returns a tickerverse and its name, from a list of command prompts
  - command prompt options:
    - *none* (does not need any)
- **io_support.py**
  - `get_current_symbols` looks for stock ticker symbols in the files within directory
  - `memory_check` verifies if file occupies too much space in RAM
  - `merge_chunked` inner-joins a small dataframe (left) with a large one (right), the latter being read in chunks
  - `write_as_append` writes dataframe to file path in append mode
  - command prompt options:
    - *none* (does not need any)
- **ticker_universe.py**
  - `obtain_parse_nasdaq` gets the Nasdaq 100 stocks from stockmonitor.com. 
  - `obtain_parse_wiki` gets either the S&P 500 or the Dow 30 stocks from Wikipedia. 
  - `obtain_parse_mutual_funds` gets the top 25 mutual funds from marketwatch.com.
  - `obtain_parse_etfs` gets the top 100 ETFs from etfdb.com.
  - command prompt options:
    - *none* (does not need any)
- **return_calculator.py**
  - `get_rolling_returns` calculates a list of rolling returns on an asset or portfolio
  - `overall_returns` calculates the overall return from start to finish
  - command prompt options:
    - *none* (does not need any)
- **plotter.py**
  - `feature_plot` plots a file of features as a correlation heatmap
  - `price_plot` plots a single asset against any number of prices, trends, indicators, etc.
  - command prompt options:
    - `-symbol`: symbol of the asset to plot
    - `-folderPath`: location of folder to look for files
    - `-function`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
    - `-startDate`: start date of data to plot
    - `-endDate`: end date of aforementioned
    - `-column`: choice of price or volume to plot
- **technicals_calculator.py**
  - `aroon` returns the Aroon indicator of asset data
  - `aroon_oscillator` returns the Aroon oscillator of asset data
  - `average_price` returns the average price of asset data
  - `average_true_range` returns the average true range of asset data
  - `bollinger` returns the Bollinger bands and width thereof, for asset data
  - `chande_momentum_oscillator` returns the Chande momentum oscillator of a price input
  - `dema` returns the "double" exponential moving average of input
  - `directional_index` returns the directional indices (+DI and -DI) of asset data
  - `directional_movt_index` returns the directional movement index (based directly on +DI and -DI) of asset data
  - `ease_of_movt` returns the ease of movement of asset data
  - `exponential_moving_average` returns the exponential moving average of input
  - `general_stochastic` returns the general Stochastic indicator of a price input
  - `macd` returns the MACD of a price input (same as price oscillator with 26-period slow EMA and 12-period fast EMA)
  - `median_price` returns the median price of asset data
  - `normalized_price` returns the baseline-normalized price (a.k.a. performance indicator) of a price input
  - `on_balance_volume` returns the on balance volume of asset data
  - `parabolic_sar` returns the parabolic SAR of asset data
  - `percent_volume_oscillator` returns the percent volume oscillator of volume data
  - `price_channel` returns the high and low price channels of a price input
  - `price_oscillator` returns the price oscillator of a price input, which depends on a choice of moving average function
  - `qstick` returns the Q-stick indicator of asset data, which depends on a choice of moving average function
  - `rel_momentum_index` returns the relative momentum index of a price input (typically closing price)
  - `rel_strength_index` returns the one-day relative momentum index of a price input
  - `simple_moving_average` returns the simple moving average of input
  - `stochastic_oscillator` returns the stochastic oscillator of asset data, which depends on a choice of moving average function
  - `triangular_moving_average` returns the triangular moving average of input
  - `true_range` returns the true range of asset data
  - `typical_price` returns the typical price of asset data
  - `variable_moving_average` returns the variable moving average of a price input
  - `weighted_close` returns the weighted close of asset data
  - `zero_lag_ema` returns the "zero-lag" exponential moving average of a price input
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
