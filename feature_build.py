## This code builds files of ML features on equity data.
## Author: Miguel Opeña
## Version: 1.1.2

import logging
import sys
import time

import command_parser as cmd
import download
import io_support as io
import plotter
import technicals as ti

FORMAT = '%(asctime)-15s %(user)-8s %(levelname)s:%(message)s'
logging.basicConfig(filename='/Users/openamiguel/Desktop/LOG/example.log', level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)
logger.info("----------INITIALIZING NEW RUN OF {}----------".format(__name__))

def get_features(tick_data, price, baseline):
	""" Compiled function with all possible features added to it.
		Inputs: asset data, column to use as price, baseline asset/index
		Outputs: dataframe of features
	"""
	price_with_trends = tick_data
	price_with_trends['AccumSwing1000'] = ti.accum_swing(tick_data, limit=1000)
	price_with_trends['AD_line'] = ti.ad_line(tick_data)
	price_with_trends['ADX30'] = ti.adx(tick_data, num_periods=30)
	price_with_trends['ADXR30'] = ti.adxr(tick_data, num_periods=30)
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
	price_with_trends['Chaikin30'] = ti.chaikin(tick_data, num_periods=30)
	price_with_trends['ChaikinADOsc'] = ti.chaikin_ad_osc(tick_data)
	price_with_trends['ChaikinVol30'] = ti.chaikin_volatility(tick_data, num_periods=30)
	price_with_trends['CMO30'] = ti.chande_momentum_oscillator(price, num_periods=30)
	price_with_trends['DEMA30'] = ti.dema(price)
	di_positive, di_negative = ti.directional_index(tick_data, num_periods=30)
	price_with_trends['DIPLUS_30'] = di_positive
	price_with_trends['DIMINUS_30'] = di_negative
	logger.debug(list(price_with_trends.columns.values))
	price_with_trends['DPO30'] = ti.detrended_price_osc(price, num_periods=30)
	price_with_trends['DX30'] = ti.directional_movt_index(tick_data, num_periods=30)
	price_with_trends['DSI'] = ti.dynamic_momentum_index(price)
	price_with_trends['ease_of_movt'] = ti.ease_of_movt(tick_data, constant=10000000)
	price_with_trends['EMA30'] = ti.exponential_moving_average(price)
	price_with_trends['generalStoch30'] = ti.general_stochastic(price, num_periods=30)
	mcd, macdPct = ti.macd(price)
	price_with_trends['KO'] = ti.klinger_osc(tick_data)
	price_with_trends['MACD'] = mcd
	price_with_trends['MACDPct'] = macdPct
	price_with_trends['MarketFacIndex'] = ti.market_fac_index(tick_data)
	price_with_trends['MassIndex30'] = ti.mass_index(tick_data, num_periods=30)
	price_with_trends['medianPrice'] = ti.median_price(tick_data)
	price_with_trends['momentum'] = ti.momentum(price)
	mf, mfi, mfr = ti.money_flow_index(tick_data, num_periods=14)
	price_with_trends['MoneyFlow'] = mf
	price_with_trends['MoneyFlowIndex'] = mfi
	price_with_trends['MoneyFlowRatio_14'] = mfr
	price_with_trends['NVI'] = ti.negative_volume_index(tick_data)
	price_with_trends['normalizedPrice'] = ti.normalized_price(price, baseline.close)
	price_with_trends['OBV'] = ti.on_balance_volume(tick_data)
	price_with_trends['PFE14'] = ti.polarized_fractal_efficiency(tick_data, num_periods=14)
	price_with_trends['PFE30'] = ti.polarized_fractal_efficiency(tick_data, num_periods=30)
	price_with_trends['PSAR'] = ti.parabolic_sar(tick_data)
	price_with_trends['PVO_30_14'] = ti.percent_volume_oscillator(tick_data.volume, num_periods_slow=30, num_periods_fast=14)
	hichannel, lochannel = ti.price_channel(price, num_periods=30)
	price_with_trends['PriceChannelHigh'] = hichannel
	price_with_trends['PriceChannelLow'] = lochannel
	logger.debug(list(price_with_trends.columns.values))
	# priceOscVMA, priceOscVMAPct = ti.price_oscillator(price, ti.variable_moving_average, num_periods_slow=30, num_periods_fast=14)
	# price_with_trends['PriceOscVMA_30_14'] = priceOscVMA
	# price_with_trends['PriceOscVMAPct_30_14'] = priceOscVMAPct
	priceOscSMA, priceOscSMAPct = ti.price_oscillator(price, ti.simple_moving_average, num_periods_slow=30, num_periods_fast=14)
	price_with_trends['PriceOscSMA_30_14'] = priceOscSMA
	price_with_trends['PriceOscSMAPct_30_14'] = priceOscSMAPct
	# priceOscTMA, priceOscTMAPct = ti.price_oscillator(price, ti.triangular_moving_average, num_periods_slow=30, num_periods_fast=14)
	# price_with_trends['PriceOscTMA_30_14'] = priceOscTMA
	# price_with_trends['PriceOscTMAPct_30_14'] = priceOscTMAPct
	priceOscEMA, priceOscEMAPct = ti.price_oscillator(price, ti.exponential_moving_average, num_periods_slow=30, num_periods_fast=14)
	price_with_trends['PriceOscEMA_30_14'] = priceOscEMA
	price_with_trends['PriceOscEMAPct_30_14'] = priceOscEMAPct
	priceOscZLEMA, priceOscZLEMAPct = ti.price_oscillator(price, ti.zero_lag_ema, num_periods_slow=30, num_periods_fast=14)
	price_with_trends['PriceOscZLEMA_30_14'] = priceOscZLEMA
	price_with_trends['PriceOscZLEMAPct_30_14'] = priceOscZLEMAPct
	logger.debug(list(price_with_trends.columns.values))
	price_with_trends['PROC'] = ti.price_rate_of_change(price)
	price_with_trends['PVI'] = ti.positive_volume_index(tick_data)
	price_with_trends['PV_rank'] = ti.price_volume_rank(tick_data)
	price_with_trends['PVT'] = ti.price_volume_trend(tick_data)
	# price_with_trends['QstickVMA_30'] = ti.qstick(tick_data, ti.variable_moving_average, num_periods=30)
	price_with_trends['QstickSMA_30'] = ti.qstick(tick_data, ti.simple_moving_average, num_periods=30)
	price_with_trends['QstickEMA_30'] = ti.qstick(tick_data, ti.exponential_moving_average, num_periods=30)
	price_with_trends['QstickZLEMA_30'] = ti.qstick(tick_data, ti.zero_lag_ema, num_periods=30)
	# price_with_trends['QstickTMA_30'] = ti.qstick(tick_data, ti.triangular_moving_average, num_periods=30)
	price_with_trends['RI30'] = ti.range_indicator(tick_data, num_periods=30)
	price_with_trends['RMI30'] = ti.rel_momentum_index(price, num_periods=30)
	price_with_trends['RSI'] = ti.rel_strength_index(price)
	price_with_trends['RVI14'] = ti.rel_vol_index(price, num_periods=14)
	price_with_trends['RVI30'] = ti.rel_vol_index(price, num_periods=30)
	price_with_trends['SMA30'] = ti.simple_moving_average(price)
	logger.debug(list(price_with_trends.columns.values))
	price_with_trends['SMI14'] = ti.stochastic_momentum_index(tick_data, num_periods=14)
	"""
	fastDVMA, slowDVMA = ti.stochastic_oscillator(price, ti.variable_moving_average, num_periods=30)
	price_with_trends['FastDStochasticOscVMA_30'] = fastDVMA
	price_with_trends['FastDStochasticOscVMA_30'] = slowDVMA
	"""
	fastDSMA, slowDSMA = ti.stochastic_oscillator(price, ti.simple_moving_average, num_periods=30)
	price_with_trends['FastDStochasticOscSMA_30'] = fastDSMA
	price_with_trends['FastDStochasticOscSMA_30'] = slowDSMA
	fastDEMA, slowDEMA = ti.stochastic_oscillator(price, ti.exponential_moving_average, num_periods=30)
	price_with_trends['FastDStochasticOscEMA_30'] = fastDEMA
	price_with_trends['FastDStochasticOscEMA_30'] = slowDEMA
	fastDZLEMA, slowDZLEMA = ti.stochastic_oscillator(price, ti.zero_lag_ema, num_periods=30)
	price_with_trends['FastDStochasticOscZLEMA_30'] = fastDZLEMA
	price_with_trends['FastDStochasticOscZLEMA_30'] = slowDZLEMA
	# fastDTMA, slowDTMA = ti.stochastic_oscillator(price, ti.triangular_moving_average, num_periods=30)
	# price_with_trends['FastDStochasticOscTMA_30'] = fastDTMA
	# price_with_trends['FastDStochasticOscTMA_30'] = slowDTMA
	price_with_trends['Swing1000'] = ti.swing_index(tick_data, limit=1000)
	price_with_trends['T3'] = ti.tee_three(price, num_periods=30)
	price_with_trends['T4'] = ti.tee_four(price, num_periods=30)
	price_with_trends['TMA30'] = ti.triangular_moving_average(price)
	price_with_trends['TEMA30'] = ti.triple_ema(price)
	price_with_trends['TR'] = ti.true_range(tick_data)
	price_with_trends['TRIX14'] = ti.trix(price, num_periods=14)
	price_with_trends['TRIX30'] = ti.trix(price, num_periods=30)
	price_with_trends['TS14'] = ti.trend_score(price, num_periods=14)
	price_with_trends['TS30'] = ti.trend_score(price, num_periods=30)
	price_with_trends['TSI14'] = ti.true_strength_index(price, num_periods=14)
	price_with_trends['TSI30'] = ti.true_strength_index(price, num_periods=30)
	price_with_trends['TypicalPrice'] = ti.typical_price(tick_data)
	price_with_trends['UO'] = ti.ultimate_oscillator(tick_data)
	price_with_trends['VAMA30'] = ti.vol_adj_moving_average(tick_data, num_periods=30)
	price_with_trends['VHF30'] = ti.vertical_horizontal_filter(tick_data, num_periods=30)
	price_with_trends['VMA30'] = ti.variable_moving_average(price, num_periods=30)
	price_with_trends['WeightedClose'] = ti.weighted_close(tick_data)
	price_with_trends['WilliamsAD'] = ti.williams_ad(tick_data)
	price_with_trends['WilliamsR30'] = ti.williams_percent(tick_data, num_periods=30)
	price_with_trends['WMA30'] = ti.weighted_moving_average(tick_data.close, num_periods=30)
	price_with_trends['ZLEMA30'] = ti.zero_lag_ema(price, num_periods=30)
	return price_with_trends

def main():
	""" User interacts with program through command prompt. 
		Example prompts: 
		
			python technicals_calculator.py -tickerUniverse AAPL,MSFT,GS,F,GOOG,AMZN -baseline ^^GSPC -startDate 2014-01-01 -endDate 2018-06-28 -timeSeriesFunction DAILY -folderPath C:/Users/Miguel/Documents/EQUITIES/stockDaily
		
		Inputs: implicit through command prompt
		Outputs: 0 if everything works
	"""
	prompts = sys.argv
	## Handles where the user wants to download their files. 
	# Default folder path is relevant to the author only. 
	folder_path = cmd.get_generic_from_prompts(prompts, query="-folderPath", default="/Users/openamiguel/Documents/EQUITIES/stockDaily", req=False)
	## Handles which symbol(s) the user wants to process.
	tickerverse, name = cmd.get_tickerverse_from_prompts(prompts, folderpath=folder_path)
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
	current_symbols = io.get_current_symbols(folder_path + "/features")
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