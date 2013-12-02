import pickle
from naivebayes import *
import pdb


class Bayes:

	def __init__(self):
		self.w_nb = None
		self.k_nb = None
		self.threshold = 0.7

	def unpickle_obj(self, filename):
		f = open(filename, "r")
		obj = pickle.load(f)
		f.close()
		return obj

	def initialize_bayes(self):
		self.w_nb = self.unpickle_obj('data/bayes_model/time_nb.obj')
		self.k_nb = self.unpickle_obj('data/bayes_model/weather_nb.obj')

	def classify_with_bayes(self, tweet):
		time_result = self.w_nb.classify_top(tweet)
		weather_result = self.k_nb.classify_all(tweet, self.threshold)
		return weather_result, time_result
