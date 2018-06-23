# equitysim

Harnesses the AlphaVantage API to pull, store, plot, and analyze equity data on the big players: any member of the S&P 500, Dow 30, or NASDAQ 100 indices, as well as any of the 100 most-traded ETFs and the top 25 most-traded mutual funds. 

See [the AlphaVantage documentation](https://www.alphavantage.co/documentation/) for more details on how API calls work within this code! 

## documentation of each file and its methods

### assorted calculators and misc. programs
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
  - `sharpe_ratio` calculates the Sharpe ratio for a given portfolio
    - proxy for risk-free rate is the 3-month US T-bill
  - `portfolio_valuation` values the portfolio (initial value, final value, and return) against a benchmark (such as an index)
  - command prompt options:
    - *none* (does not need any)
- **technicals_calculator.py**
  - `SMA` returns the simple moving average of input
- **plotter.py**
  - `price_plot` plots the performance of an asset price against a price-related trend and a (possibly price-related) baseline
  - `portfolio_plot` plots the performance of a portfolio against a benchmark (such as an index)
  - command prompt options:
    - `-symbol`: symbol of the asset to plot
    - `-folderPath`: location of folder to look for files
    - `-timeSeriesFunction`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
    - `-startDate`: start date of data to plot
    - `-endDate`: end date of aforementioned
    
    
### AlphaVantage data download/update suite
- **single_download.py**
  - `fetch_symbol` downloads and processes a single symbol from AlphaVantage.
  - `fetch_symbol_from_drive` retrieves a single symbol from local drive
  - command prompt options: 
    - `-symbol`: symbol of the asset to download
    - `-folderPath`: location of folder to store file
    - `-apiKey`: AlphaVantage API key to download files from AlphaVantage (user-specific)
    - `-timeSeriesFunction`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
- **prelim_download.py**
  - `download_separate` pulls data on a ticker universe in the form of separate files, each named after the ticker symbol and the time series function
    - separate files contain as much data as AlphaVantage can offer
  - `download_combined` pulls data on a ticker universe in the form of one combined file, named after the ticker universe and the time series function
    - *combined files contain closing price data only*
  - command prompt options:
    - `-tickerUniverse`: collection of tickers to download (can also be a CSV of ticker symbols) 
    - `-folderPath`: location of folder to store file
    - `-separate`: download files separately
    - `-combined`: download files in a combined fashion
    - `-apiKey`: AlphaVantage API key (user-specific)
    - `-timeSeriesFunction`: distinguishes between intraday, daily, weekly, etc. downloads
    - `-interval` specifies what kind of intraday (1min, 15min, etc.)
- **auto_update.py**
  - `update_separate` updates a collection of separately downloaded files with the latest data from AlphaVantage
  - `update_combined` updates a combined file with the latest data from AlphaVantage
  - command prompt options:
    - `-folderPath`: location of folder to look for files
    - `-apiKey`: AlphaVantage API key (user-specific)
    
### simulator suite
- **ranking_simulator.py**
  - `asset_ranker` returns two segments of a ticker universe (long positions and short positions) based on ranking metric
  - `portfolio_generator` builds a portfolio around the aforementioned long and short positions
  - **note:** requires that one download files using the code first; this will not read from AlphaVantage
  - command prompt options:
    - `-tickerUniverse`: collection of tickers to rank
    - `-folderPath`: location of folder to look for files
    - `-baseline`: asset or index (typically latter) to use as performance baseline
    - `-startRankDate`: start date of data to generate ranking with
    - `-endRankDate`: end date of aforementioned
    - `-startTestDate`: start date of trading the ranking portfolio
    - `-endTestDate`: end date of aforementioned
    - `-lowQuant`: lower cutoff for the quantiles
    - `-highQuant`: higher cutoff for the quantiles
    - `-switchPos`: option to swap the long and short portfolios
    - `-showPlot`: option to show the portfolio plot
    - `-plotName`: name of the plot image file
    - `-numShares`: number of shares to trade at each transaction (long or short)
- **meanrev_simulator.py**
  - `crossover` emulates a strategy where buy/sell signals occur when one trend (ex. 30-day moving average) crosses a baseline trend (ex. 90-day moving average)
  - `zscore_distance` emulates a strategy where buy/sell signals occur when one trend (ex. asset price) deviates too far from a baseline trend (ex. 90-day moving average), as measured by z-scores
  - **note:** requires that one download files using the code first; this will not read from AlphaVantage
  - command prompt options: 
    - `-symbol`: symbol of the asset to trade
    - `-folderPath`: location of folder to look for files
    - `-baseline`: asset or index (typically latter) to use as performance baseline (default: S&P500 index)
    - `-startDate`: start date of trading given stock
    - `-endDate`: end date of aforementioned
    - `-showPlot`: option to show the portfolio plot
    - `-plotName`: name of the plot image file
    - `-numShares`: number of shares to trade at each transaction (long or short)
    - `-startValue`: initial value of portfolio (USD)
    - `-numShares`: number of shares to trade at each transaction (long or short)
