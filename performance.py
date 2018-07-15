## This code assesses portfolios from portfolio.py using risk metrics and return plots. 
## Author: Miguel Opeña
## Version: 1.4.3

import logging
import numpy as np
import pandas as pd

import download
import plotter
import portfolio
import return_calculator
import strategy
import technicals as ti

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def beta(price, baseline):
    """ Calculates the Sharpe ratio of the given asset/portfolio against baseline.
        Inputs: price Series, baseline Series
        Outputs: beta of portfolio
    """
    price_baseline = pd.concat([price, baseline], axis=1)
    price_baseline.columns = ['price', 'baseline']
    cov = price_baseline.cov()
    var = baseline.var()
    return cov.baseline[0] / var

def sharpe_ratio(portfolio, risk_free_rate=1.94):
    """ Calculates the Sharpe ratio of the given portfolio.
        Inputs: portfolio Series, risk-free interest rate
        Outputs: Sharpe ratio of portfolio
    """
    price = portfolio.values.tolist()
    returns = np.array(return_calculator.get_rolling_returns(price))
    # Uses the classic formula for Sharpe
    sharpe = (returns.mean() - risk_free_rate) / (returns.std())
    return sharpe

def treynor_ratio(portfolio, baseline, risk_free_rate=1.94):
    """ Calculates the Treynor ratio of the given portfolio.
        Inputs: portfolio Series, baseline Series, risk-free interest rate
        Outputs: Treynor ratio of portfolio
    """
    price = portfolio.values.tolist()
    price_returns = np.array(return_calculator.get_rolling_returns(price))
    treynor = (price_returns.mean() - risk_free_rate) / np.array(beta(price, baseline))
    return treynor

def returns_valuation(portfolio, baseline):
    """    Values the portfolio against a baseline, such as an index. 
        Inputs: portfolio and baseline Series over time
        Outputs: the portfolio's initial value, final value, overall returns; the baseline's returns
    """
    # Calculate start value, end value, returns on portfolio, and returns on baseline
    initial_value = portfolio[0]
    final_value = portfolio[-1]
    returns = return_calculator.overall_returns(portfolio.values.tolist())
    baseline_returns = return_calculator.overall_returns(baseline.values.tolist())
    return initial_value, final_value, returns, baseline_returns

def main():
    symbol="AAPL"
    folder_path="/Users/openamiguel/Documents/EQUITIES/stockDaily"
    start_date = "2010-01-05"
    end_date = "2018-06-28"
    tick_data = download.load_single_drive(symbol, folderpath=folder_path)
    tick_data = tick_data[start_date:end_date]
    prices = pd.concat([tick_data.close], axis=1)
    trend = ti.simple_moving_average(tick_data.close, num_periods=30)
    baseline = ti.simple_moving_average(tick_data.close, num_periods=90)
    trend_baseline = pd.concat([trend, baseline], axis=1)
    trend_baseline.columns = ['trend','baseline']
    trades = strategy.zscore_distance(trend_baseline)
    port = portfolio.apply_trades(prices, trades)

    portfolio_baseline = download.load_single_drive("^GSPC", folderpath=folder_path)
    portfolio_baseline = portfolio_baseline[start_date:end_date]

    start_value, end_value, returns, baseline_returns = returns_valuation(port.price, portfolio_baseline.close)

    logger.info("Starting portfolio value: {}".format(start_value))
    logger.info("Ending portfolio value: {}".format(end_value))
    logger.info("Return on this strategy: {}".format(returns))
    logger.info("Return on S&P500 index: {}".format(baseline_returns))
    logger.info("Sharpe ratio: {}".format(sharpe_ratio(port.price)))

    # Plots the portfolio
    plot_name = "Strategy01"
    port_price = pd.concat([port.price, portfolio_baseline.close], axis=1)
    port_price.columns = ['portfolio', 'baseline']
    plotter.price_plot(port_price, symbol=plot_name, folderpath=folder_path, subplot=[True,True], returns=[True,True], showPlot=True)


if __name__ == "__main__":
    main()