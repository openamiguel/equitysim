# equitysim

Harnesses the AlphaVantage API to pull, store, plot, and analyze equity data on the big players: any member of the S&P 500, Dow 30, or NASDAQ 100 indices. 

### documentation of each file and its methods

- ticker_universe.py
  - `obtain_parse_nasdaq` gets the Nasdaq 100 stocks from stockmonitor.com. 
  - `obtain_parse_wiki` gets either the S&P 500 or the Dow 30 stocks from Wikipedia. 
  - command prompt options:
    - *none* (does not need any)
- portfolio_calculator.py
  - `portfolio_plot` plots the performance of a portfolio against a benchmark (such as an index)
  - `portfolio_valuation` values the portfolio (initial value, final value, and return) against a benchmark (such as an index)
  - command prompt options:
    - *none* (does not need any)
- single_download.py
  - `download_symbol` downloads and processes a single symbol from AlphaVantage. 
  - command prompt options: 
    - `-symbol`: symbol of the asset to download
    - `-folderPath`: location of folder to store file
    - `-apiKey`: AlphaVantage API key to download files from AlphaVantage (user-specific)
    - `-timeSeriesFunction`: distinguishes between intraday, daily, weekly, etc. downloads
- prelim_download.py
  - `download_separate` pulls data on a ticker universe in the form of separate files, each named after the ticker symbol and the time series function
    - separate files contain as much data as AlphaVantage can offer
  - `download_combined` pulls data on a ticker universe in the form of one combined file, named after the ticker universe
    - *combined files contain closing price data only*
  - command prompt options:
    -`-tickerUniverse`: collection of tickers to download (can also be a CSV of ticker symbols) 
    -`-folderPath`: location of folder to store file
    -`-separate`: download files separately
    -`-combined`: download files in a combined fashion
    -`-apiKey`: AlphaVantage API key (user-specific)
    -`timeSeriesFunction`: distinguishes between intraday, daily, weekly, etc. downloads
- autoupdate.py
  - `update_separate` updates a collection of separately downloaded files with the latest data from AlphaVantage
  - `update_combined` updates a combined file with the latest data from AlphaVantage
  - command prompt options:
    -`-folderPath`: location of folder to look for files
    -`-apiKey`: AlphaVantage API key (user-specific)
- ranking_simulator.py
- meanrev_simulator.py
