## This code builds files of ML features on equity data.
## Author: Miguel Opeña
## Version: 1.0.0

import logging
import sys
import time

import command_parser as cmd
import download
import io_support as io
import plotter
import technicals as ti

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_features(tick_data, price, baseline):
    """ Compiled function with all indicators in the file added to it.
        Inputs: asset data, column to use as price, baseline asset/index
        Outputs: dataframe of features
    """
    price_with_trends = tick_data
    aroon_up, aroon_down = ti.aroon(tick_data)
    price_with_trends['aroonUp25'] = aroon_up
    price_with_trends['aroonDown25'] = aroon_down
    price_with_trends['aroonOsc25'] = ti.aroon_oscillator(tick_data)
    logger.debug(list(price_with_trends.columns.values))
    price_with_trends['averagePrice'] = ti.average_price(tick_data)
    price_with_trends['ATR14'] = ti.average_true_range(tick_data)
    lowband, midband, hiband, width = ti.bollinger(tick_data)
    price_with_trends['BollingerLow'] = lowband
    price_with_trends['BollingerMid'] = midband
    price_with_trends['BollingerHigh'] = hiband
    price_with_trends['CMO30'] = ti.chande_momentum_oscillator(price, num_periods=30)
    price_with_trends['DEMA30'] = ti.dema(price)
    di_positive, di_negative = directional_index(tick_data, num_periods=30)
    price_with_trends['DIPLUS_30'] = di_positive
    price_with_trends['DIMINUS_30'] = di_negative
    logger.debug(list(price_with_trends.columns.values))
    price_with_trends['DX30'] = directional_movt_index(tick_data, num_periods=30)
    price_with_trends['ease_of_movt'] = ease_of_movt(tick_data, constant=10000000)
    price_with_trends['EMA30'] = exponential_moving_average(price)
    price_with_trends['generalStoch30'] = general_stochastic(price, num_periods=30)
    mcd, macdPct = macd(price)
    price_with_trends['MACD'] = mcd
    price_with_trends['MACDPct'] = macdPct
    price_with_trends['medianPrice'] = median_price(tick_data)
    price_with_trends['normalizedPrice'] = normalized_price(price, baseline.close)
    price_with_trends['OBV'] = on_balance_volume(tick_data)
    price_with_trends['PSAR'] = parabolic_sar(tick_data)
    price_with_trends['PVO_30_14'] = percent_volume_oscillator(tick_data.volume, num_periods_slow=30, num_periods_fast=14)
    hichannel, lochannel = price_channel(price, num_periods=30)
    price_with_trends['PriceChannelHigh'] = hichannel
    price_with_trends['PriceChannelLow'] = lochannel
    logger.debug(list(price_with_trends.columns.values))
    priceOscVMA, priceOscVMAPct = price_oscillator(price, variable_moving_average, num_periods_slow=30, num_periods_fast=14)
    price_with_trends['PriceOscVMA_30_14'] = priceOscVMA
    price_with_trends['PriceOscVMAPct_30_14'] = priceOscVMAPct
    priceOscSMA, priceOscSMAPct = price_oscillator(price, simple_moving_average, num_periods_slow=30, num_periods_fast=14)
    price_with_trends['PriceOscSMA_30_14'] = priceOscSMA
    price_with_trends['PriceOscSMAPct_30_14'] = priceOscSMAPct
    priceOscTMA, priceOscTMAPct = price_oscillator(price, triangular_moving_average, num_periods_slow=30, num_periods_fast=14)
    price_with_trends['PriceOscTMA_30_14'] = priceOscTMA
    price_with_trends['PriceOscTMAPct_30_14'] = priceOscTMAPct
    priceOscEMA, priceOscEMAPct = price_oscillator(price, exponential_moving_average, num_periods_slow=30, num_periods_fast=14)
    price_with_trends['PriceOscEMA_30_14'] = priceOscEMA
    price_with_trends['PriceOscEMAPct_30_14'] = priceOscEMAPct
    priceOscZLEMA, priceOscZLEMAPct = price_oscillator(price, zero_lag_ema, num_periods_slow=30, num_periods_fast=14)
    price_with_trends['PriceOscZLEMA_30_14'] = priceOscZLEMA
    price_with_trends['PriceOscZLEMAPct_30_14'] = priceOscZLEMAPct
    logger.debug(list(price_with_trends.columns.values))
    price_with_trends['QstickVMA_30'] = qstick(tick_data, variable_moving_average, num_periods=30)
    price_with_trends['QstickSMA_30'] = qstick(tick_data, simple_moving_average, num_periods=30)
    price_with_trends['QstickEMA_30'] = qstick(tick_data, exponential_moving_average, num_periods=30)
    price_with_trends['QstickZLEMA_30'] = qstick(tick_data, zero_lag_ema, num_periods=30)
    price_with_trends['QstickTMA_30'] = qstick(tick_data, triangular_moving_average, num_periods=30)
    price_with_trends['RMI30'] = rel_momentum_index(price, num_periods=30)
    price_with_trends['RSI'] = rel_strength_index(price)
    price_with_trends['SMA30'] = simple_moving_average(price)
    logger.debug(list(price_with_trends.columns.values))
    """
    fastDVMA, slowDVMA = stochastic_oscillator(price, variable_moving_average, num_periods=30)
    price_with_trends['FastDStochasticOscVMA_30'] = fastDVMA
    price_with_trends['FastDStochasticOscVMA_30'] = slowDVMA
    """
    fastDSMA, slowDSMA = stochastic_oscillator(price, simple_moving_average, num_periods=30)
    price_with_trends['FastDStochasticOscSMA_30'] = fastDSMA
    price_with_trends['FastDStochasticOscSMA_30'] = slowDSMA
    fastDEMA, slowDEMA = stochastic_oscillator(price, exponential_moving_average, num_periods=30)
    price_with_trends['FastDStochasticOscEMA_30'] = fastDEMA
    price_with_trends['FastDStochasticOscEMA_30'] = slowDEMA
    fastDZLEMA, slowDZLEMA = stochastic_oscillator(price, zero_lag_ema, num_periods=30)
    price_with_trends['FastDStochasticOscZLEMA_30'] = fastDZLEMA
    price_with_trends['FastDStochasticOscZLEMA_30'] = slowDZLEMA
    fastDTMA, slowDTMA = stochastic_oscillator(price, triangular_moving_average, num_periods=30)
    price_with_trends['FastDStochasticOscTMA_30'] = fastDTMA
    price_with_trends['FastDStochasticOscTMA_30'] = slowDTMA
    price_with_trends['TMA30'] = triangular_moving_average(price)
    price_with_trends['TR'] = true_range(tick_data)
    price_with_trends['TypicalPrice'] = typical_price(tick_data)
    price_with_trends['VMA30'] = variable_moving_average(price, num_periods=30)
    price_with_trends['WeightedClose'] = weighted_close(tick_data)
    price_with_trends['ZLEMA30'] = zero_lag_ema(price, num_periods=30)
    return price_with_trends

def main():
    """ User interacts with program through command prompt. 
        Example prompts: 
        
            python technicals_calculator.py -tickerUniverse AAPL,MSFT,GS,F,GOOG,AMZN -baseline ^^GSPC -startDate 2014-01-01 -endDate 2018-06-28 -timeSeriesFunction DAILY -folderPath C:/Users/Miguel/Documents/EQUITIES/stockDaily
        
        Inputs: implicit through command prompt
        Outputs: 0 if everything works
    """
    prompts = sys.argv
    ## Handles which symbol(s) the user wants to process.
    tickerverse, name = cmd.get_tickerverse_from_prompts(prompts)
    ## Handles where the user wants to download their files. 
    # Default folder path is relevant to the author only. 
    folder_path = cmd.get_generic_from_prompts(prompts, query="-folderPath", default="C:/Users/Miguel/Documents/EQUITIES/stockDaily", req=False)
    ## Handles which index/asset should be the baseline 
    baseline_symbol = cmd.get_generic_from_prompts(prompts, query="-baseline", default="^GSPC", req=False)
    ## Handles collection of the start and end dates for trading
    start_date = cmd.get_generic_from_prompts(prompts, query="-startDate")
    end_date = cmd.get_generic_from_prompts(prompts, query="-endDate")
    ## Handles the desired time series function. 
    function = cmd.get_generic_from_prompts(prompts, query="-function")
    ## Handles the special case: if INTRADAY selected. 
    interval = cmd.get_generic_from_prompts(prompts, query="-interval") if function == "INTRADAY" else ""
    ## Checks if user wants to plot only, not to process features data
    plot_only = "-plotOnly" in prompts
    # Gets the baseline data
    baseline = download.load_single_drive(baseline_symbol, function=function, interval=interval, folderpath=folder_path)
    # Gets symbols already processed
    current_symbols = io.get_current_symbols(folder_path)
    # Gets the feature data for each one
    for symbol in tickerverse:
        if plot_only:
            plotter.feature_plot(symbol, folderpath=folder_path, savePlot=True, showPlot=True)
        elif symbol not in current_symbols:
            # Download data on this symbol
            tick_data = download.load_single_drive(symbol, function=function, interval=interval, folderpath=folder_path)
            tick_data = tick_data[start_date:end_date]
            # Gets features and times the process
            logger.info("Processing {0} features...".format(symbol))
            time0 = time.time()
            price_with_trends = get_features(tick_data, tick_data.close, baseline)
            time1 = time.time()
            time_tot = time1 - time0
            logger.info("Time elapsed for %s was %4.2f seconds", symbol, time_tot)
            # This is because close is extremely correlated to open, high, and low, making them highly correlated to everything else
            price_with_trends.drop(labels=['open','high','low'], axis=1, inplace=True)
            price_with_trends.to_csv(folder_path + "/features/" + symbol + "_Features.csv")

if __name__ == "__main__":
    main()