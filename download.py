## This code contains the re-consolidated download functions, and can perform any one of the following tasks:
## Download one stock (one-stock-one-file) from API, load one stock (one-stock-one-variable) from local drive, download many stocks (one-stock-one-file) from API, or load many stocks (many-stocks-one-variable) from local drive
## Author: Miguel Opeña
## Version: 1.0.0

import pandas as pd
import time
import sys

import command_parser
import ticker_universe

# Start of the URL for AlphaVantage queries
MAIN_URL = "https://www.alphavantage.co/query?"
# Delay prevents HTTP 503 errors (AlphaVantage recommends 10, but 15 works in practice)
DELAY = 15

