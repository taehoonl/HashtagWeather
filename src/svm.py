import os
import pdb

import numpy as np
import svmlight
import svmlight_loader as svml

from parser import Parser

class SVM:

	def __init__(self):
		self.parser = Parser()
		self.weather_models = []
		self.time_models = []
		self.is_weather_model = None
		self.default_data_features = []
		self.data = None
		self.index = None
		self.index_map = None

	def initialize_svm(self):
		# get file path, depending on the location from which the class is called
		cwd = os.getcwd()
		cwd = cwd.split('/')
		if cwd[len(cwd)-1] == 'src':
			index_file_path = '../data/svm/data.index'
			map_file_path = '../data/svm/data.map'
			models_file_path = '../data/svm/new_models/'
		else:
			index_file_path = 'data/svm/data.index'
			map_file_path = 'data/svm/data.map'
			models_file_path = 'data/svm/new_models/'
		self.load_all_models(models_file_path)
		if self.index is None:
			index = self.parser.load_pickled_data(index_file_path)
			index_map = self.parser.load_pickled_data(map_file_path)
			self.index = index
			self.index_map = index_map

	def load_all_models(self, path):

		filepath = path + 's5.model0.01'
		model = self.read_model(filepath)
		self.is_weather_model = model

		for i in range(4):
			filepath = path + 'new_c_w{}.model1'.format(i+1)
			model = self.read_model(filepath)
			self.time_models.append(model)

		for i in range(15):
			filepath = path + 'new_c_k{}.model0.1'.format(i+1)
			model = self.read_model(filepath)
			self.weather_models.append(model)

	def load_data(self, rel_path):
		'''
		Loads data from a SVMLight file using the svmlight_loader
		library: https://github.com/mblondel/svmlight-loader
		Returns a list of the dataset and the labels
		'''
		abs_path = os.path.abspath(rel_path)

		(x_train, labels) = svml.load_svmlight_file(abs_path)
		return [x_train, labels]

	def combine_data(self, data):
		'''
		Returns a list that combines the point coordinates
		and their labels
		'''
		print 'Combining data...'
		combined_data = []
		labels = data[1]
		data_list = np.array(data[0].todense()).tolist()
		for i in range(len(labels)):
			combined_data.append([labels[i], data_list[i]])
			if i%100 == 0:
				print 'Combined {} data'.format(i)
		return combined_data

	def format_data(self, data):
		formatted_data = []
		print 'Formatting data...'

		default_data_features = []

		for i in range(len(data[0][1])):
			default_data_features.append((i+1, 0))

		data_num = 0
		for datum in data:
			nonzero_elements = np.nonzero(datum[1])[0]
			data_features = default_data_features[:]
			# pdb.set_trace()
			for e in nonzero_elements:
				data_features[e-1] = (e+1, datum[1][e])

			if data_num%100 == 0:
				print 'Formatted {} data'.format(data_num)
			data_num += 1
			formatted_data.append((datum[0], data_features))
		return formatted_data

	def format_for_svmlight(self, data):
		combined_data = self.combine_data(data)
		formatted_data = self.format_data(combined_data)
		return formatted_data

	def format_tweet_for_svmlight(self, tweet):
		data_features = []
		word_dict = {}
		for word in tweet:
			try:
				word_dict[word] += 1
			except:
				word_dict[word] = 1
		for word in tweet:
			try:
				idx = self.index_map[word]
				data_features.append((idx, word_dict[word]))
			except:
				pass
		return [(1, data_features)]


	def read_model(self, rel_path):
		abs_path = os.path.abspath(rel_path)
		model = svmlight.read_model(abs_path)
		return model

	def train(self, data, t=0, C=1.0):
		model = svmlight.learn(data, type="classifier", t=t, C=C)
		return model

	def get_weather_tweets(self, tweets):
		weather_tweets = []
		if not isinstance(tweets, list):
			tweets = [tweets]
		for tweet in tweets:
			formatted_tweet = self.parser.stem_sentence_porter(tweet)
			formatted_tweet = self.format_tweet_for_svmlight(formatted_tweet)
			c = svmlight.classify(self.is_weather_model, formatted_tweet)
			print c
			if c[0] < 0:
				weather_tweets.append(tweet)
		return weather_tweets

	def classify(self, model, data):
		classifications = svmlight.classify(model, data)
		return classifications

	def classify_tweet(self, tweet):
		try:
			tweet = self.parser.stem_sentence_porter(tweet)
			formatted_tweet = self.format_tweet_for_svmlight(tweet)
			time_class = []
			weather_class = []
			for model in self.time_models:
				time_class.append(self.classify(model, formatted_tweet)[0])
			for model in self.weather_models:
				weather_class.append(self.classify(model, formatted_tweet)[0])
			return weather_class, time_class
		except:
			print 'You have yet to load the models.'
			print 'Please load all models with load_all_models()'
			return None


