from keras.layers import RepeatVector, Flatten
from keras.layers.core import Dropout, Dense, Activation
from keras.layers.recurrent import LSTM, GRU
from keras.models import Sequential
from keras.models import model_from_json
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import time

def open_file(file):
	df = pd.read_csv(file, sep=",\s+", header=None, engine="python")
	df = df.dropna()
	
	for item in df.columns:
		if '#' in df[item][0]:
			df = df.drop([item], axis=1)
			continue

		df[item] = df[item].map(lambda x: x.lstrip('#<>').rstrip('#<>'))
		if (df[item][0] == "e") or (df[item][0] == "i"):
			df[item] = pd.get_dummies(df[item])

		try:
			df[item] = df[item].astype(np.float64)
		except:
			continue

	#print(df.dtypes, df.shape)
	return df

def get_data(prog, data, path="/home/sachando/phase2/CSC766/data/"):
	prog_data = path + prog
	files = os.listdir(prog_data)
	#print(files)
	print(prog, data)
	x = []
	dfs = []
	for file in files:
		if data in file:
			x.append(file)
	print(x)
	for item in x:
		df = open_file(prog_data +"/" + item)
		dfs.append(df)
	return pd.concat(dfs)


def get_gen(df, window_size, stride=1, batch_size=1, sampling=1):
	print("Generating series")
	print(df.shape, df.dtypes)
	gen = TimeseriesGenerator(df.values, df.values, length=window_size , stride=stride, batch_size=batch_size, sampling_rate=sampling)
	#print(gen[0])
	return gen


def model_encdec(window_length, input_dim=2, hidden_dim=12):
	input_length = window_length
	m = Sequential()
	m.add(LSTM(units=2 * hidden_dim, activation='relu', input_shape=(input_length, input_dim), return_sequences=True))
	m.add(Dropout(rate=0.2))
#	m.add(LSTM(units=hidden_dim, activation='relu', input_shape=(input_length, input_dim), return_sequences=True))
#	m.add(Dropout(rate=0.1))
	m.add(LSTM(units=2 * hidden_dim, activation='relu', input_shape=(input_length, input_dim),return_sequences=True))
	m.add(Dropout(rate=0.2))
	m.add(Flatten())
	m.add(Dense(input_dim, activation='linear'))
	m.compile(loss='mse', optimizer='adam')
	return m

def plot_reconstruction(history):
	plt.figure(figsize=(22, 4))
	plt.plot(history['loss'])
	plt.plot(history['val_loss'])
	plt.title('model loss')
	plt.ylabel('loss')
	plt.xlabel('epoch')
	plt.legend(['train', 'valid'], loc='best')
	plt.show()
	return

class lstm_encdec():
	def __init__(self, window_size, input_dim, hidden_dim):
		
		self.model = model_encdec(window_size, input_dim, hidden_dim)
		self.window_size = window_size
		self.train_time = None
		self.update_time = 0
		self.update_count = 0
		self.input_dim = input_dim
		self.history = None
		
	def train_model(self, generator, steps=1, epochs=20, verbosity=1):

		start_time = time.time()
		earlystopper = EarlyStopping(monitor='val_loss', patience=1, verbose=0)
		history = self.model.fit_generator(generator, epochs=epochs, verbose=verbosity, callbacks=[earlystopper])
		end_time = time.time()
		self.train_time = (end_time - start_time)
		self.history = history
		return history
			
	def predict(self, data):
		return self.model.predict(data)

def evaluations(sets, modes, window_size, path="/home/sachando/phase2/CSC766/data/"):
	results="/home/sachando/phase2/CSC766/results/"
	for item in sets:
		for mode in modes:
			df = get_data(item, mode)
			_, df = train_test_split(df, test_size=0.4, shuffle=False)
			input_dim = df.shape[1]
			testgen = get_gen(df, window_size)
			filename = results + item + "_" + mode

			try:
				instance = models[item][mode]
			except KeyError:
				try:
					instance = models[item]
				except:
					models[item] = {}

				f = open(filename + ".json", 'r')
				content = f.read()
				f.close()

				loaded_model = model_from_json(content)
				loaded_model.load_weights(filename + ".hd5")
				models[item][mode] = loaded_model

			instance = models[item][mode]
			instance.compile(loss='mse', optimizer='adam')
			scores = instance.evaluate_generator(testgen)
			with open(filename + ".scores", "a") as f:
				for item in scores:
					f.write(str(item) + "\n")
	return

if __name__ == "__main__":

	path="/home/sachando/phase2/CSC766/data/"
	results="/home/sachando/phase2/CSC766/results/"

	models = {}
	sets = ["600.perlbench_s",
		"602.gcc_s",
		"605.mcf_s",
		"619.lbm_s",
		"638.imagick_s",
		"641.leela_s",
		"644.nab_s"]
	modes = ["branch", "func"]


	hidden_dim = 4
	window_size = 3
	prediction_len = 1

	l = os.listdir(results)
	if(len(l) != 0):	
		print("Trained models found")
		evaluations(sets, modes, window_size)
		raise SystemExit()

	for item in sets:
		for mode in modes:
			df = get_data(item, mode)
			input_dim = df.shape[1]
		
			df, _ = train_test_split(df, test_size=0.5, shuffle=False)
			gen = get_gen(df, window_size)
			print("Collected data for (%s, %s)" % (item, mode))
			try:
				instance = models[item][mode]
			except KeyError:
				try:
					instance = models[item]
				except:
					models[item] = {}

				p = lstm_encdec(window_size, df.shape[1], hidden_dim)
				models[item][mode] = p

			print("Training model for (%s, %s)" % (item, mode))
			instance = models[item][mode]
			instance.train_model(gen, epochs=4)
			filename = results + item + "_" + mode

			instance.model.save(filename + ".hd5")

			model_json = instance.model.to_json()
			with open(filename + ".json", "w") as json_file:
				json_file.write(model_json)

	print("All models generated and saved to results")
	evaluations(sets, modes, window_size)
