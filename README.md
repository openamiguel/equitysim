# equitysim

Harnesses the AlphaVantage API to pull, store, plot, and analyze equity data on the big players: any member of the S&P 500, Dow 30, or NASDAQ 100 indices. 

### Documentation of each file and its methods

- tick_universe.py
  - `obtain_parse_nasdaq` gets the Nasdaq 100 stocks from stockmonitor.com. 
  - `obtain_parse_wiki` gets either the S&P 500 or the Dow 30 stocks from Wikipedia. 
- portfolio_calculator.py
- single_download.py
- prelim_download.py
- autoupdate.py
- ranking_simulator.py
- meanrev_simulator.py
