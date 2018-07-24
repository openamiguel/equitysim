## This code computes a good number of technical indicators.
## Unless otherwise stated, the source for formulas is FMlabs.com.
## Author: Miguel Opeña
## Version: 1.0.12

import numpy as np
import pandas as pd

import download
import plotter

def test_technical():
	""" Hardcoded test of technical indicator """
	symbol = "AAPL"
	folderpath = "/Users/openamiguel/Documents/EQUITIES/stockDaily"
	start_date = "2015-03-01"
	end_date = "2018-06-01"
	tick_data = download.load_single_drive(symbol, folderpath=folderpath)
	tick_data = tick_data[start_date:end_date]
	ad = triple_ema(tick_data.close, num_periods=14)
	price_with_trends = pd.concat([tick_data.close, ad], axis=1)
	price_with_trends.columns = ['price', 'TEMA-14']
	plotter.price_plot(price_with_trends, symbol, subplot=[False,True,True], returns=[False,False,False], folderpath=folderpath, showPlot=True)

def ad_line(tick_data):
	""" Plots the accumulation-distribution line ("AD" or "AD line") as a measure of volume
		Inputs: dataframe with closing price, low price, high price, and volume over given timespan
		Outputs: dataframe with AD over time
	"""
	# Assumes that input is dataframe
	# Gets the close-location value index
	clv = ((tick_data.close - tick_data.low) - (tick_data.high - tick_data.close)) / (tick_data.high - tick_data.low)
	clv = clv * tick_data.volume
	ad_series = clv.cumsum()
	ad = pd.DataFrame(ad_series, columns=['ad_line'])
	return ad

def adx(tick_data, num_periods):
	""" Computes the average directional (movement) index (ADX), based on DX.
		Inputs: dataframe of data fed into the DX function
		Outputs: dataframe of ADX over time
	"""
	dx = directional_movt_index(tick_data, num_periods)
	adx = pd.DataFrame(index=dx.index, columns=['ADX'])
	# Sets the seed value to be zero
	adx.ADX[adx.index[0]] = 0
	# Walks through the data and computes ADX
	for i in range(1, len(adx.index)):
		this_date = adx.index[i]
		last_date = adx.index[i-1]
		adx.ADX[this_date] = (adx.ADX[last_date] * (num_periods - 1) + dx.DX[this_date]) / num_periods
	return adx

def adxr(tick_data, num_periods):
	""" Computes the ADX rating of a stock over time, based on ADX.
		Inputs: dataframe of data fed into the ADX function
		Outputs: dataframe of ADXR over time
	"""
	adx_df = adx(tick_data, num_periods)
	adxr = pd.DataFrame(index=adx_df.index, columns=['ADXR'])
	# Walks through the data and computes ADXR
	for i in range(0, len(tick_data.index) - num_periods):
		start_date = adx_df.index[i]
		end_date = adx_df.index[i+1]
		adxr.ADXR[end_date] = 0.5 * (adx_df.ADX[start_date] + adx_df.ADX[end_date])
	return adxr

def aroon(tick_data, num_periods=25):
	""" Computes the Aroon indicator of an asset over time. 
		This code assumes that number of periods refers to the number of periods for which data is provided, not the number of actual time periods.
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan;
			also includes number of periods to perform calculation
		Outputs: dataframes with AroonUp and AroonDown over time
	"""
	# Assume that input is dataframe
	aroon_up = pd.DataFrame(index=tick_data.index, columns=['aroon_up'])
	aroon_down = pd.DataFrame(index=tick_data.index, columns=['aroon_down'])
	# Iterates through all datewindows
	for i in range(0, len(tick_data.index) - num_periods):
		# Gets the proper tick date window
		start_date = tick_data.index[i]
		end_date = tick_data.index[i + num_periods]
		tick_data_window = tick_data[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_index = tick_data_window.close.idxmax()
		min_index = tick_data_window.close.idxmin()
		# Gets number of periods since previous extremum
		max_dist = len(tick_data[max_index:end_date]) - 1
		min_dist = len(tick_data[min_index:end_date]) - 1
		# Populates the output dataframes
		aroon_up.aroon_up[end_date] = 100 * (num_periods - max_dist) / num_periods
		aroon_down.aroon_down[end_date] = 100 * (num_periods - min_dist) / num_periods
	return aroon_up, aroon_down

def aroon_oscillator(tick_data, num_periods=25):
	""" Computes the Aroon oscillator of an asset over time, which is simply AroonUp minus AroonDown
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan;
			also includes number of periods to perform calculation
		Outputs: dataframe with Aroon oscillator over time
	"""
	# Gets AroonUp and AroonDown from the aroon function
	aroon_up, aroon_down = aroon(tick_data, num_periods=num_periods)
	aroon_up.columns = ['aroon']
	aroon_down.columns = ['aroon']
	# Initializes and populates output
	aroon_osc = pd.DataFrame(index=tick_data.index, columns=['aroon_oscillator'])
	aroon_osc = aroon_up.subtract(aroon_down,axis=1)
	# Returns Aroon oscillator
	return aroon_osc

def average_price(tick_data):
	""" Computes the average price of an asset over time. 
		Inputs: dataframe with opening price, closing price, high price, low price over given timespan
		Outputs: average price over given timespan
	"""
	# Assume that input is dataframe
	avg_price = pd.DataFrame(index=tick_data.index, columns=['average_price'])
	# Adds up the prices into avg_price
	avg_price['average_price'] = tick_data.open + tick_data.close + tick_data.high + tick_data.low
	# Divides by four
	avg_price = avg_price.divide(4)
	return avg_price

def average_true_range(tick_data, num_periods=14):
	""" Uses the true range to compute the average true range (ATR) of an asset over time.
		Inputs: data on high, low, and close of asset over given timespan
		Outputs: ATR indicator
	"""
	# Sets up dataframe for true range
	tr = pd.DataFrame(index=tick_data.index, columns=["true_range"])
	for i in range(1, len(tick_data.index)):
		# Gets the date window (not dependent on num_periods)
		now_date = tick_data.index[i]
		last_date = tick_data.index[i-1]
		# Adds this true range to the dataframe
		tr.true_range[now_date] = max(tick_data.high[now_date], tick_data.close[last_date]) - max(tick_data.low[now_date], tick_data.close[last_date])
	# Sets up dataframe for average true range
	atr = pd.DataFrame(index=tick_data.index, columns=["ATR"])
	# The seed value is NOT zero
	atr.ATR[atr.index[0]] = tr.true_range.mean()
	for i in range(1, len(tr.index)):
		# Gets the date window (not dependent on num_periods)
		now_date = tr.index[i]
		last_date = tr.index[i-1]
		# Adds this true range to the dataframe
		atr.ATR[now_date] = (atr.ATR[last_date] * (num_periods - 1) + tr.true_range[now_date]) / num_periods
	# Returns ATR
	return atr

def bollinger(tick_data, num_periods=20, num_deviations=2):
	""" Computes the Bollinger bands and width of an asset over time. 
		Inputs: dataframe with closing price, high price, low price over given timespan
		Outputs: Bollinger bands and width over given timespan
	"""
	# Calculates typical price and standard deviation thereof
	typ_price = typical_price(tick_data)
	stdev = typ_price['typical_price'].std()
	# Calculates the three Bollinger bands
	midband = simple_moving_average(typ_price, num_periods=num_periods)
	lowband = midband - num_deviations * stdev
	hiband = midband + num_deviations * stdev
	# Calculates the width of said bands
	width = 2 * num_deviations * stdev
	# Returns all the needed information
	return lowband, midband, hiband, width

def chande_momentum_oscillator(price, num_periods):
	""" Computes the Chande momentum oscillator of a price input over time.
		Inputs: price of asset, number of periods in CMO
		Outputs: CMO of price
	"""
	up_df = pd.DataFrame(index=price.index, columns=['upp'])
	dn_df = pd.DataFrame(index=price.index, columns=['down']) 
	cmo = pd.DataFrame(index=price.index, columns=['CMO'])
	# Walks through the dates and gets up/down indices at each interval
	for i in range(0, len(price.index) - 1):
		# Gets the proper tick date window
		start_date = price.index[i]
		end_date = price.index[i+1]
		# Gets some more variables
		up = 0
		dn = 0
		if price[end_date] > price[start_date]: 
			up = price[end_date] - price[start_date]
		else: 
			dn = price[start_date] - price[end_date]
		# Saves up and down accordingly
		up_df.upp[end_date] = up
		dn_df.down[end_date] = dn
	# Walks through up and down to get cmo
	for i in range(0, len(price.index) - num_periods):
		start_date = price.index[i]
		end_date = price.index[i + num_periods]
		# Walks backward by num_periods to get sum
		ups = up_df.upp[start_date:end_date].sum()
		downs = dn_df.down[start_date:end_date].sum()
		# Saves CMO
		cmo.CMO[end_date] = 100 * (ups - downs) / (ups + downs)
	return cmo

def chaikin(tick_data, num_periods):
	""" Computes the Chaikin money flow (volume indicator) of a stock over time.
		Inputs: dataframe with closing price, low price, high price, volume; number of periods
		Outputs: Chaikin money flow over given timespan
	"""
	# Builds the closing location value index and multiplies by volume
	clv = ((tick_data.close - tick_data.low) - (tick_data.high - tick_data.close)) / (tick_data.high - tick_data.low)
	clv_vol = clv * tick_data.volume
	chk = pd.DataFrame(index=tick_data.index, columns=['chaikin'])
	# Iterates through the prices using given window
	for i in range(0, len(tick_data.index) - num_periods):
		start_date = tick_data.index[i]
		end_date = tick_data.index[i + num_periods]
		chk.chaikin[end_date] = clv_vol[start_date:end_date].sum() / tick_data.volume[start_date:end_date].sum()
	return chk

def chaikin_ad_osc(tick_data):
	""" Computes the Chaikin A/D oscillator over given timespan.
		Very related to the Chaikin money flow, in that CLV is used.
		Inputs: dataframe with closing price, low price, high price, volume
		Outputs: Chaikin A/D oscillator over given timespan
	"""
	ad = ad_line(tick_data)
	component1 = exponential_moving_average(ad.ad_line, num_periods=3)
	component2 = exponential_moving_average(ad.ad_line, num_periods=10)
	return component1 - component2

def chaikin_volatility(tick_data, num_periods):
	""" Computes the Chaikin volatility over given timespan.
		Related in principle to the other Chaikin indicators.
		Inputs: dataframe with low and high price; number of periods
		Outputs: Chaikin volatility over given timespan
	"""
	emahl = exponential_moving_average(tick_data.high - tick_data.low, num_periods=num_periods)
	cv = pd.DataFrame(index=tick_data.index, columns=['ChkVol'])
	for i in range(0, len(tick_data.index) - num_periods):
		start_date = tick_data.index[i]
		end_date = tick_data.index[i + num_periods]
		cv.ChkVol[end_date] = 0.01 * (emahl[end_date] - emahl[start_date]) / emahl[start_date]
	return cv

def dema(input_values, num_periods=30):
	""" Computes the so-called double exponential moving average (DEMA) of a time series over certain timespan.
		Inputs: input values, number of periods in DEMA
		Outputs: DEMA over given timespan
	"""
	# If input is Series, output is Dataframe
	if isinstance(input_values, pd.Series):
		ema = exponential_moving_average(input_values, num_periods=num_periods)
		ema2 = exponential_moving_average(ema, num_periods=num_periods)
		dema = pd.DataFrame(index=input_values.index, columns=['DEMA'])
		# This is the formula for DEMA
		for i in range(0, len(input_values.index)):
			dema.DEMA[i] = 2 * ema[i] - ema2[i]
		return dema
	# If input is list, output is list
	elif isinstance(input_values, list):
		ema = np.array(exponential_moving_average(input_values, num_periods=num_periods))
		ema2 = np.array(exponential_moving_average(exponential_moving_average(input_values, num_periods=num_periods), num_periods=num_periods))
		# This is the formula for DEMA
		dema = 2 * ema - ema2
		return dema.tolist()
	else:
		raise ValueError("Unsupported data type given as input to dema in technicals_calculator.py")
		return None

def detrended_price_osc(price, num_periods):
	""" Computes the detrended price oscillator (DPO). 
		Related to detrended price in principle only; actual method is dissimilar. 
		Inputs: price Series over time; number of periods in DPO
		Outputs: DPO over given timespan
	"""
	dpo = pd.DataFrame(index=price.index, columns=['DPO'])
	for i in range(1, len(dpo.index) - num_periods):
		start_date = dpo.index[i]
		last_price = price[dpo.index[i + num_periods - 1]]
		end_date = dpo.index[i + num_periods]
		# Subtracts the previous price in the window by the moving avg of price
		sma = simple_moving_average(price[start_date:end_date], 
						num_periods=num_periods)
		dpo.DPO[end_date] = last_price - sma[sma.index[-1]] / num_periods
	return dpo

def directional_index(tick_data, num_periods):
	""" Computes the directional indices (+DI and -DI).
		Inputs: close, high, and low data on asset; number of periods
		Outputs: +DI and -DI on asset over given timespan
	"""
	# Initializes starting variables
	di_positive = pd.DataFrame(index=tick_data.index, columns=['DI_PLUS'])
	di_negative = pd.DataFrame(index=tick_data.index, columns=['DI_MINUS'])
	# Initializes running sums
	plus_dm_sum = 0
	minus_dm_sum = 0
	tr_sum = 0
	# Walks through the price dataframe
	for i in range(1, len(tick_data.index)):
		now_date = tick_data.index[i]
		last_date = tick_data.index[i-1]
		# Gets starting variables
		delta_high = tick_data.high[last_date] - tick_data.high[now_date]
		delta_low = tick_data.low[now_date] - tick_data.low[last_date]
		plus_dm = delta_high if delta_high > delta_low else 0
		minus_dm = delta_low if delta_high < delta_low else 0
		tr = max(tick_data.high[now_date], tick_data.close[last_date]) - max(tick_data.low[now_date], tick_data.close[last_date])
		# Updates running sums
		plus_dm_sum = plus_dm_sum - (plus_dm_sum / num_periods) + plus_dm
		minus_dm_sum = minus_dm_sum - (minus_dm_sum / num_periods) + minus_dm
		tr_sum = tr_sum - (tr_sum / num_periods) + tr
		# Updates output dataframe
		di_positive.DI_PLUS[now_date] = 100 * plus_dm_sum / tr_sum
		di_negative.DI_MINUS[now_date] = 100 * minus_dm_sum / tr_sum
	# Return output
	return di_positive, di_negative

def directional_movt_index(tick_data, num_periods):
	""" Computes the directional movement index (DX), which is derived directly from +DI and -DI.
		Inputs: close, high, and low data on asset; number of periods
		Outputs: DX on asset over given timespan
	"""
	di_positive, di_negative = directional_index(tick_data, num_periods)
	di_positive.columns = ['DX']
	di_negative.columns = ['DX']
	return (di_positive - di_negative) / (di_positive + di_negative)

def dynamic_momentum_index(price):
	""" Computes the dynamic momentum index, the DSI, of a price over time.
		Inputs: price Series over time (typically close)
		Outputs: DSI dataframe over time
	"""
	stdev_5 = price.rolling(5).std()
	numerator = 14 * simple_moving_average(stdev_5, num_periods=10)
	return numerator  / stdev_5

def ease_of_movt(tick_data, constant=1000000000):
	""" Computes the ease of movement indicator (EMV). The constant is set to 1e+9 for plotting purposes. 
		Inputs: dataframe with high price, low price, and volume over given timespan; constant in the box ratio calculation
		Outputs: EMV over given timespan
	"""
	# Initializes empty dataframe to hold EMV values
	emv = pd.DataFrame(index=tick_data.index, columns=['EMV'])
	for i in range(1, len(tick_data.index)):
		# Calculates the midpoint move and box ratio at current time
		midpoint_move = (tick_data.high[i] - tick_data.low[i] - (tick_data.high[i-1] - tick_data.low[i-1])) / 2
		box_ratio = (tick_data.volume[i] / constant) / (tick_data.high[i] - tick_data.low[i])
		# Calculates EMV from the previous variables
		emv.EMV[i] = midpoint_move / box_ratio
	return emv

def exponential_moving_average(input_values, num_periods=30):
	""" Computes the exponential moving average (EMA) of a time series over certain timespan.
		Inputs: input values, number of periods in EMA
		Outputs: EMA over given timespan
	"""
	K = 2 / (num_periods + 1)
	inputs_refined = input_values.fillna(0)
	# If input is Series, output is Dataframe
	if isinstance(inputs_refined, pd.Series):
		ema = pd.Series(inputs_refined[0], index=inputs_refined.index)
		# Iterates through and populates dataframe output
		for i in range(1, len(inputs_refined.index)):
			ema[i] = ema[i-1] + K * (inputs_refined[i] - ema[i-1])
		return ema
	# If input is list, output is list
	elif isinstance(inputs_refined, list):
		ema = [inputs_refined[0]]
		# Iterates through and populates list output
		for i in range(1, len(inputs_refined)):
			ema.append(ema[i-1] + K * (inputs_refined[i] - ema[i-1]))
		return ema
	else:
		raise ValueError("Unsupported data type given as input to exponential_moving_average in technicals_calculator.py")
		return None

def general_stochastic(price, num_periods):
	""" Computes the General Stochastic calculation of an asset over time. 
		Inputs: series with price over given timespan
		Outputs: General Stochastic over given timespan
	"""
	# Assume that input is dataframe
	general_stoch = pd.DataFrame(index=price.index, columns=['general_stochastic'])
	# Iterates through all datewindows
	for i in range(0, len(price.index) - num_periods):
		# Gets the proper tick date window
		start_date = price.index[i]
		end_date = price.index[i + num_periods]
		price_window = price[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_price = price_window.max()
		min_price = price_window.min()
		# Populates the output dataframes
		general_stoch.general_stochastic[end_date] = (price[end_date] - min_price) / (max_price - min_price)
	return general_stoch

def macd(price):
	""" Computes the MACD of a time series over certain timespan, which is essentially price oscillator for 26 and 12 periods, with EMA. 
		Inputs: price input
		Outputs: MACD over given timespan
	"""
	return price_oscillator(price, exponential_moving_average, num_periods_slow=26, num_periods_fast=12)

def median_price(tick_data):
	""" Computes the median price of an asset over time. 
		Inputs: dataframe with high and low price over given timespan
		Outputs: median price over given timespan
	"""
	# Assume that input is dataframe
	med_price = pd.DataFrame(index=tick_data.index, columns=['median_price'])
	# Adds up the prices into med_price
	med_price['median_price'] = tick_data.high + tick_data.low
	# Divides by two
	med_price = med_price.divide(2)
	return med_price

def normalized_price(price, baseline):
	""" Computes the normalized price (aka performance indicator) against a baseline.
		Inputs: price series and baseline series
		Outputs: normalized price over given timespan
	"""
	norm_price = 100 * (price - baseline) / baseline
	norm_price.columns = ['normalized_price']
	return norm_price

def on_balance_volume(tick_data):
	""" Computes the on-balance volume (OBV) of an asset over time
		Inputs: volume series
		Outputs: OBV indicator
	"""
	obv = pd.DataFrame(0, index=tick_data.index, columns=['OBV'])
	for i in range(1, len(tick_data.index)):
		# Gets current window of time
		now_date = tick_data.index[i]
		last_date = tick_data.index[i-1]
		# Three conditions to consider when updating OBV
		if tick_data.close[now_date] > tick_data.close[last_date]:
			obv.OBV[now_date] = obv.OBV[last_date] + tick_data.volume[now_date]
		elif tick_data.close[now_date] > tick_data.close[last_date]:
			obv.OBV[now_date] = obv.OBV[last_date] - tick_data.volume[now_date]
		else:
			obv.OBV[now_date] = obv.OBV[last_date]
	return obv

def parabolic_sar(tick_data, accel_start=0.02, accel_thresh=0.2, accel_step=0.02):
	""" Computes the parabolic SAR of an asset over time. 
		Source: https://www.tradinformed.com/2014/03/24/calculate-psar-indicator-using-excel/
		Inputs: dataframe with high, low, and closing price over given timespan
		Outputs: parabolic SAR over given timespan
	"""
	# Initializes timestamp and start date variables
	timestamp = tick_data.index
	start_date = timestamp[0]
	# Initializes the seed values for parabolic SAR
	accel = accel_start
	is_falling = True
	extreme_point = tick_data.low[start_date]
	initial_psar = 0
	# Fills PSAR dataframe with seed value
	psar = pd.DataFrame(index=timestamp, columns=['PSAR'])
	psar.PSAR[start_date] = tick_data.high[start_date]
	for i in range(1, len(timestamp)):
		# Gets the date now, the last date, and the date before that
		now_date = timestamp[i]
		last_date = timestamp[i-1]
		# Safeguard for the first iteration, when i == 1
		farther_date = timestamp[i-2] if i > 1 else last_date
		difference = psar.PSAR[last_date] - extreme_point * accel
		# Saves last extreme point for incrementing accel
		last_extreme_point = extreme_point
		# Falling parabolic SAR calculation
		if is_falling:
			initial_psar = max(psar.PSAR[last_date] - difference, tick_data.high[last_date], tick_data.high[farther_date])
			psar.PSAR[now_date] = initial_psar if tick_data.high[now_date] < initial_psar else extreme_point
			extreme_point = min(extreme_point, tick_data.low[now_date])
		# Rising parabolic SAR calculation
		else:
			initial_psar = max(psar.PSAR[last_date] - difference, tick_data.low[last_date], tick_data.low[farther_date])
			psar.PSAR[now_date] = initial_psar if tick_data.low[now_date] > initial_psar else extreme_point
			extreme_point = max(extreme_point, tick_data.high[now_date])
		# Compares previous and current state of is_falling to increment accel properly
		last_is_falling = is_falling
		is_falling = tick_data.close[now_date] > psar.PSAR[now_date]
		# Conditional updates and checks on accel
		if last_is_falling == is_falling:
			if last_extreme_point != extreme_point and accel < accel_thresh:
				accel = accel + accel_step
			else:
				accel = accel_thresh
		else: 
			accel = accel_start
	return psar

def percent_volume_oscillator(volume, num_periods_slow, num_periods_fast):
	""" Computes the percent volume oscillator of an asset over time
		Inputs: choice of function, price input, number of periods for slow MA, number of periods for fast MA
		Outputs: price oscillator over given timespan
	"""
	# Gets the fast EMA of volume
	fast_ema = exponential_moving_average(volume, num_periods=num_periods_fast)
	# Gets the slow EMA of volume
	slow_ema = exponential_moving_average(volume, num_periods=num_periods_slow)
	pct_vol_osc = 100 * (fast_ema - slow_ema) / fast_ema
	return pct_vol_osc

def price_channel(price, num_periods):
	""" Computes the price channels (recent maximum and minimum) of an asset over time.
		Inputs: Series of price over given timespan
		Outputs: high channel and low channel over given timespan
	"""
	# Assume that input is dataframe
	hichannel = pd.DataFrame(index=price.index, columns=['high_channel'])
	lochannel = pd.DataFrame(index=price.index, columns=['low_channel'])
	# Iterates through all datewindows
	for i in range(0, len(price.index) - num_periods):
		# Gets the proper tick date window
		start_date = price.index[i]
		end_date = price.index[i + num_periods]
		price_window = price[start_date:end_date]
		# Gets the recent maximum and minimum relative to the date window
		max_price = price_window.max()
		min_price = price_window.min()
		# Populates the output dataframes
		hichannel.high_channel[end_date] = max_price
		lochannel.low_channel[end_date] = min_price
	return hichannel, lochannel

def price_oscillator(price, moving_avg, num_periods_slow, num_periods_fast):
	""" Computes the price oscillator of a time series over certain timespan, which depends on a choice of moving average function.
		Inputs: choice of function, price input, number of periods for slow MA, number of periods for fast MA
		Outputs: price oscillator over given timespan
	"""
	price_osc = moving_avg(price, num_periods_slow) - moving_avg(price, num_periods_fast)
	price_osc_percent = 100 * price_osc / moving_avg(price, num_periods_fast)
	return price_osc, price_osc_percent

def price_volume_index(tick_data):
	""" Computes a coefficient on close price, with increments only if volume is increasing
		Closely related to the NVI indicator
		Inputs: volume and closing price
		Outputs: PVI indicator over given timespan
	"""
	pvi = pd.DataFrame(index=tick_data.index, columns=['PVI'])
	pvi.PVI[pvi.index[0]] = 0
	for i in range(1, len(tick_data.index) - 1):
		start_date = pvi.index[i - 1]
		end_date = pvi.index[i]
		# Indicator increments if volume has increased
		increment = (tick_data.close[end_date] - tick_data.close[start_date]) / tick_data.close[start_date] if tick_data.volume[end_date] > tick_data.volume[start_date] else 0
		pvi.PVI[end_date] = pvi.PVI[start_date] + increment
	return pvi

def positive_volume_trend(tick_data):
	""" Computes the price-volume trend (PVT), which directly depends on price and volume data.
		Related closely to on-balance volume (OBV)
		Inputs: volume and closing price
		Outputs: PVT indicator over given timespan
	"""
	pvt = pd.DataFrame(index=tick_data.index, columns=['PVT'])
	pvt.PVT[pvt.index[0]] = 0
	for i in range(1, len(tick_data.index) - 1):
		start_date = pvt.index[i - 1]
		end_date = pvt.index[i]
		# Indicator accounts for volume and closing price
		pvt.PVT[end_date] = pvt.PVT[start_date] + tick_data.volume[end_date] * (tick_data.close[end_date] - tick_data.close[start_date]) / tick_data.close[start_date]
	return pvt

def qstick(tick_data, moving_avg, num_periods):
	""" Computes the Q-stick indicator of asset data over certain timespan, which depends on a choice of moving average function.
		Inputs: choice of function, dataframe with close and open price over time
		Outputs: price oscillator over given timespan
	"""
	return moving_avg(tick_data.close - tick_data.open, num_periods)

def rel_momentum_index(price, num_periods):
	""" Computes the relative momentum index of a (closing) price dataset given the number of periods.
		Inputs: price Series (close), number of periods
		Outputs: RMI of closing price
	"""
	# Assume that input is dataframe/Series
	rmi = pd.DataFrame(index=price.index, columns=['RMI'])
	# Gets the variables used in computing at all time points
	upavg = 0
	dnavg = 0
	for i in range(0, len(price.index) - num_periods):
		# Gets the proper tick date window
		start_date = price.index[i]
		end_date = price.index[i + num_periods]
		# Gets some more variables
		up = 0
		dn = 0
		if price[end_date] > price[start_date]: 
			up = price[end_date] - price[start_date]
		else: 
			dn = price[start_date] - price[end_date]
		# Updates upavg and dnavg
		upavg = (upavg * (num_periods - 1) + up) / num_periods
		dnavg = (dnavg * (num_periods - 1) + dn) / num_periods
		# Computes the RMI
		rmi.RMI[end_date] = 100 * upavg / (upavg + dnavg)
	return rmi

def rel_strength_index(price):
	return rel_momentum_index(price, num_periods=14)

def simple_moving_average(input_values, num_periods=30):
	""" Computes the simple moving average (SMA) of a time series over certain timespan.
		Inputs: input values, number of periods in SMA
		Outputs: SMA over given timespan
	"""
	# Computes the rolling mean (default: 30-day and 90-day)
	sma = input_values.rolling(num_periods).mean()
	sma.columns = ['SMA' + str(num_periods)]
	return sma

def stochastic_oscillator(tick_data, moving_avg, num_periods):
	""" Computes the Stochastic oscillator of an asset over time. 
		Inputs: series with price over given timespan, number of periods to look back, type of moving average to apply
		Outputs: Stochastic oscillator over given timespan
	"""
	percent_k = 100 * general_stochastic(tick_data, num_periods=num_periods)
	percent_k.columns = ['PctK']
	percent_k_smoothed = moving_avg(percent_k.PctK, num_periods)
	fast_d = moving_avg(percent_k.PctK, num_periods)
	slow_d = moving_avg(percent_k_smoothed, num_periods)
	return fast_d, slow_d

def stochastic_rsi(price):
	""" Computes the general Stochastic of the RSI.
		Inputs: price data
		Outputs: stochastic RSI over given timespan
	"""
	rsi = rel_strength_index(price)
	srsi = general_stochastic(rsi, num_periods=14)
	return srsi

def tee_three(input_values, num_periods, vfactor=0.7):
	""" Computes the third generalized DEMA  of an input value. Formally called T3, but
		that would have been an unstylish function name.
		Inputs: input values, factor weight of double ema in the "GD" function
		Outputs: T3 averaging method of input over time
	"""
	# GD is the generalized DEMA function
	def gd(in_val, vfactor=vfactor):
		return exponential_moving_average(in_val, num_periods=num_periods) * (1 + vfactor) - exponential_moving_average(exponential_moving_average(in_val, num_periods=num_periods), num_periods=num_periods) * vfactor
	return gd(gd(gd(input_values)))

def tee_four(input_values, num_periods, vfactor=0.7):
	""" Computes the fourth generalized DEMA of an input value. Formally called T4, but
		that would have been an unstylish function name.
		Inputs: input values, factor weight of double ema in the "GD" function
		Outputs: T4 averaging method of input over time
	"""
	# GD is the generalized DEMA function
	def gd(in_val, vfactor=vfactor):
		return exponential_moving_average(in_val, num_periods=num_periods) * (1 + vfactor) - exponential_moving_average(exponential_moving_average(in_val, num_periods=num_periods), num_periods=num_periods) * vfactor
	return gd(gd(gd(gd(input_values))))

def triangular_moving_average(input_values, num_periods=30):
	""" Computes the triangular moving average (TMA) of a time series over certain timespan, which weighs the middle values more.
		Inputs: input values, number of periods in TMA
		Outputs: TMA over given timespan
	"""
	periods = num_periods if num_periods % 2 == 0 else num_periods + 1
	per1 = int(periods / 2 + 1)
	tma = simple_moving_average(input_values, num_periods=per1)
	per2 = per1 - 1
	tma = simple_moving_average(tma, num_periods=per2)
	return tma

def triple_ema(input_values, num_periods=30):
	""" Computes the triple exponential moving average (TEMA) of a time series over certain timespan, which weighs the middle values more.
		Inputs: input values, number of periods in TEMA
		Outputs: TEMA over given timespan
	"""
	term1 = 3 * exponential_moving_average(input_values, num_periods=num_periods)
	term2 = 3 * exponential_moving_average(exponential_moving_average(input_values, num_periods=num_periods), num_periods=num_periods)
	term3 = exponential_moving_average(exponential_moving_average(exponential_moving_average(input_values, num_periods=num_periods), num_periods=num_periods), num_periods=num_periods)
	return term1 - term2 + term3

def true_range(tick_data):
	""" Computes the true range of an asset over time.
		Inputs: dataframe wtih closing price, high price, and low price
		Outputs: true range over given timespan
	"""
	# Initializes output as empty dataframe
	trange = pd.DataFrame(index=tick_data.index, columns=['true_range'])
	for i in range(1, len(tick_data.index)):
		# Gets the current and previous date
		this_date = tick_data.index[i]
		last_date = tick_data.index[i-1]
		# Gets the three possibilities for true range
		option1 = abs(tick_data.high[this_date] - tick_data.low[this_date])
		option2 = abs(tick_data.high[this_date] - tick_data.close[last_date])
		option3 = abs(tick_data.low[this_date] - tick_data.close[last_date])
		# Filters based on which is largest
		trange.true_range[this_date] = max(option1,option2,option3)
	return trange

def typical_price(tick_data):
	""" Computes the typical price of an asset over time. 
		Inputs: dataframe with closing price, high price, low price over given timespan
		Outputs: average price over given timespan
	"""
	# Assume that input is dataframe
	typ_price = pd.DataFrame(index=tick_data.index, columns=['typical_price'])
	# Adds up the prices into typ_price
	typ_price['typical_price'] = tick_data.close + tick_data.high + tick_data.low
	# Divides by three
	typ_price = typ_price.divide(3)
	return typ_price

def variable_moving_average(price, num_periods=30):
	""" Computes the variable moving average, weights based on volatility, in this case CMO
		Inputs: price series and number of periods (default: 30)
		Outputs: VMA indicator
	"""
	# Initializes smoothing constant
	smoothing_constant = 2 / (num_periods + 1)
	# Volatility is the 9-period CMO
	cmo = chande_momentum_oscillator(price, num_periods=9)
	vma = pd.DataFrame(index=price.index, columns=['VMA'])
	for i in range(1, len(price.index)):
		# Gets the current and previous date
		now_date = price.index[i]
		last_date = price.index[i-1]
		# Fills the output dataframe
		vma.VMA[now_date] = smoothing_constant * cmo.CMO[now_date] * price[now_date] + (1 - smoothing_constant * cmo.CMO[now_date]) * price[last_date]
	# Returns output dataframe
	return vma

def weighted_close(tick_data):
	""" Computes the weighted closing price of an asset over time. 
		Inputs: dataframe with closing price, high price, low price over given timespan
		Outputs: weighted closing price over given timespan
	"""
	# Assume that input is dataframe
	weighted_close_price = pd.DataFrame(index=tick_data.index, columns=['weighted_close_price'])
	# Adds up the prices into weighted_close_price
	weighted_close_price['weighted_close_price'] = tick_data.close + tick_data.close + tick_data.high + tick_data.low
	# Divides by four
	weighted_close_price = weighted_close_price.divide(4)
	return weighted_close_price

def zero_lag_ema(price, num_periods):
	""" Computes the so-called zero lag exponential moving average, which substracts older data to minimize cumulative effect.
		Inputs: price Series, number of periods to run calculation on
		Outputs: zero-lag EMA
	"""
	lag = int((num_periods - 1) / 2)
	ema = pd.Series(index=price.index)
	# Iterates through all datewindows
	for i in range(0, len(price.index) - lag):
		# Computes the de-lagged data
		lag_date = price.index[i]
		now_date = price.index[i + lag]
		price_window = price[lag_date:now_date]
		ema[now_date] = 2 * price_window[now_date] - price_window[lag_date]
	zlema = exponential_moving_average(ema, num_periods=num_periods)
	zlema.name = 'ZLEMA'
	return zlema

test_technical()