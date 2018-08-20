# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:32:13 2017

Discussed in https://towardsdatascience.com/deep-learning-in-finance-9e088cb17c03.

@author: sonaam1234 on Github
repo: sonaam1234/DeepLearningInFinance/ReturnPrediction/ReturnPrediction_LSTM.py

Extensively modified by author of this repository. 
"""
import numpy as np
import pandas as pd
from keras.layers.core import Dense, Activation
from keras.layers.recurrent import LSTM
from keras.models import Sequential
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

from download import CLoader

# Code to initialize logger
LOGDIR = "/Users/openamiguel/Desktop/LOG"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Set file path for logger
handler = logging.FileHandler('{}/equitysim_download.log'.format(LOGDIR))
handler.setLevel(logging.DEBUG)
# Format the logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# Add the new format
logger.addHandler(handler)
# Format the console logger
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)
# Add the new format to the logger file
logger.addHandler(consoleHandler)

# Set general parameters
SEED = 42
np.random.seed(SEED)
FOLDERPATH = '/Users/openamiguel/Documents/EQUITIES/stockDaily'
COL_TO_PREDICT = 'close'
TRAIN_DATE = "2016-01-01"
PLOT_DATE = "2018-03-01"

# Set neural network parameters
LOOK_BACK = 12
NUM_EPOCHS = 300
BATCH_SIZE = 80

def load_input_data(symbol, start_date):
	""" Assembles input data from multiple sources.
		For now, the only source is a single OHCLV dataframe. 
		Inputs: symbol name, start date to get data for
		Outputs: dataframe of symbol data from start date to present
	"""
	# Reads the stock data as a Pandas dataframe
	loader = CLoader(folderpath=FOLDERPATH)
	df = loader.load_single_drive(symbol=symbol)
	# Filters a specific start date for analysis
	logger.debug("Isolating all data before start date...")
	df = df[start_date:]
	# TODO: in order to add more input data, concatenate time series inputs column-wise with the OHLCV dataframe
	logger.info("Input data successfully isolated!")
	return df

def get_predictors(df, blacklist=[]):
	""" Adds a column with suffix "_ret" for each predictor in df.
		Inputs: dataframe to find and add predictors, blacklist of columns to not touch
		Outputs: list of predictor columns, dataframe with new columns
	"""
	logger.info("Retrieving predictor columns...")
	predictors = []
	# Adds a new column with suffix "_ret" for each column in df
	for col in df.columns:
		# Skips the blacklist of columns
		if any([x == col for x in blacklist]):
			continue
		df[col + '_ret'] = df[col].pct_change().fillna(0)
		# Saves each new column
		predictors.append(col + '_ret')
	logger.info("Predictor columns retrieved!")
	# Returns list of predictors and dataframe with new columns
	return predictors, df

def transform(df, column):
	""" Transforms a column in a dataframe using scikit-learn's Standard Scaler.
		Inputs: dataframe to modify, column to transform
		Outputs: dataframe of the single transformed column (not the whole dataframe!)
	"""
	logger.info("Transforming column {}...".format(column))
	sc = StandardScaler()
	df_col_aslist = df.as_matrix(columns=[column])
	df_col_aslist = sc.fit_transform(df_col_aslist)
	df_col = pd.DataFrame(df_col_aslist)
	df_col.columns = [column]
	logger.info("Column {} successfully transformed!".format(column))
	return sc, df_col

def transform_all_cols(df, column):
	""" Retrieves transformed versions of all columns in a dataframe. 
		Additionally returns the StandardScaler used for a choice column (i.e. the main column.)
		Inputs: dataframe to transform, column to get StandardScaler from
		Outputs: dataframe with each column transformed
	"""
	logger.info("Starting to transform all columns in input dataframe...")
	sc_choice = None
	# Iterates through each column
	for col in df.columns:
		# Skips the "_ret" suffixed columns
		if "_ret" not in str(col):
			sc, df.loc[:, col] = transform(df, col=col)
			# Looks for the choice column and saves its StandardScaler
			if col == column:
				logger.info("Found and saved standard scaler for choice column {}...".format(column))
				sc_choice = sc
	# Returns the StandardScaler object and the transformed dataframe
	logger.info("All columns transformed!")
	return sc_choice, df

def build_train(df):
	""" Returns sets X, y as inputs into the neural network. 
		Filters input based on all data before training date. 
		Inputs: dataframe input, training date
		Outputs: lists of training data
	"""
	logger.info("Building training data...")
	train_df = df[:TRAIN_DATE]
	timeseries = np.asarray(train_df[COL_TO_PREDICT + '_ret'])
	timeseries = np.atleast_2d(timeseries)
	if timeseries.shape[0] == 1:
			timeseries = timeseries.T
	X = np.atleast_3d(np.array([timeseries[start:start + LOOK_BACK] for start in range(0, timeseries.shape[0] - LOOK_BACK)]))
	y = timeseries[LOOK_BACK:]
	logger.info("Training data built!")
	# Returns the training data
	return X, y

def build_model():
	""" Constructs the architecture of the neural network model. 
		Currently a two-cell LSTM with a linear activation function, mean square error, 
			and RMSProp optimizer.
		Feel free to explore various architectures!
		Inputs: none
		Outputs: model object built by Keras
	"""
	logger.debug("Constructing model object...")
	model = Sequential()
	model.add(LSTM(input_shape = (1,), input_dim=1, output_dim=6, return_sequences=True))
	model.add(LSTM(input_shape = (1,), input_dim=1, output_dim=6, return_sequences=False))
	model.add(Dense(1))
	model.add(Activation('linear'))
	model.compile(loss="mse", optimizer="rmsprop")
	logger.debug("Model object constructed!")
	return model

def get_predictions(df, predictors, colname='prediction'): 
	""" Predicts the time series progression for all dates after training.
		Inputs: dataframe to predict, predictor columns, and name of column to add
		Outputs: 
	"""
	logger.info("Starting to predict {} data after training date...".format(COL_TO_PREDICT))
	# Adds the predicted price column
	df[colname] = df.loc[df.index[0], COL_TO_PREDICT + '_ret']
	# Builds the predicted price column
	for i in range(len(df.index)):
		# Skips any dates before the lookback range, or before the train date
		if i <= LOOK_BACK or df.index[i] < TRAIN_DATE:
			continue
		# Informs user of current progress
		logger.info("Analyzing date {}".format(str(df.index[i])))
		a = None
		# Iterates through all predictors and uses their data to predict COL_TO_PREDICT
		for pred in predictors:
			logger.debug("Utilizing {} predictor...".format(pred))
			b = df.loc[df.index[i-LOOK_BACK:i], pred].as_matrix()
			a = b if a is None else np.append(a, b)
		# Gets the model's prediction and reshapes it before adding to output
		y = model.predict(a.reshape(1, LOOK_BACK * len(predictors), 1))
		df.loc[df.index[i], colname] = y[0][0]
	logger.info("Successfully predicted {} data!".format(COL_TO_PREDICT))
	return df

def plot_results(df, sc_choice, colname='prediction', showPlot=True, savePlot=False):
	""" Plots the data in Matplotlib, given user choice of an inital plot date.
		Inputs: dataframe of output data, chosen scaler object (to reverse normalization), 
			column name of predictions, order to show plot, order to save plot
		Outputs: none
	"""
	logger.info("Starting to process data for plotting...")
	# Isolates the plotting data based on desired plot date
	df_plot = df[PLOT_DATE:]
	# Processes COL_TO_PREDICT using the chosen scaler noted previously
	logger.info("Processing the {} column...".format(COL_TO_PREDICT))
	df_plot.loc[:, COL_TO_PREDICT] = sc_choice.inverse_transform(df_plot.loc[:, COL_TO_PREDICT + '_ret'])
	# Processes COL_TO_PREDICT using the chosen scaler noted previously
	logger.info("Processing the prediction column...")
	df_plot.loc[:, colname] = sc_choice.inverse_transform(df_plot.loc[:, 'prediction'])
	# Plots the data
	plt.plot(df_plot[COL_TO_PREDICT], 'b')
	plt.plot(df_plot.prediction, 'g')
	logger.info("Data successfully plotted!")
	# Saves the plot if desired
	if savePlot:
		fig_file_path = FOLDERPATH + "/images/" + symbol + "_LSTM.png"
		plt.savefig(fig_file_path)
	# Shows the plot if desired
	if showPlot:
		plt.show()
	return

def main():
	# Load input data
	df = load_input_data(symbol='AMZN', start_date='2010-01-01')
	# Get predictor columns
	predictors, df = get_predictors(df)
	# Transform columns
	sc_choice, df = transform_all_cols(df, column=COL_TO_PREDICT)
	# Build training data and model
	X, y = build_train(df)
	model = build_model()
	# Fit the model
	model.fit(X, y, epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, verbose=1, shuffle=False)
	# Make predictions
	df = get_predictions(df, predictors)
	# Save these predictions
	df.to_csv('/Users/openamiguel/Desktop/LSTM_Output.csv')
	# Plot results
	plot_results(df, sc_choice)

if __name__ == "__main__":
	main()
