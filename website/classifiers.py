import pdb, pickle, os

from src.svm import SVM
from src.naivebayes import MultiNaiveBayes, NaiveBayes
import src.naivebayes
from src.init_bayes import Bayes
from src.dtree import DecisionTree
from src.node import Node
from src.query_tweet import Query

class Classifiers:

	def __init__(self):
		self.threshold = 0.7
		self.weather_labels = ["clouds", "cold", "dry", "hot", "humid", "hurricane",
							   "I can't tell", "ice", "other", "rain", "snow", "storms",
							   "sun", "tornado", "wind"]
		self.weather_code = ["N", "G", "dry", "1", "humid", "hurricane",
							   "I can't tell", "G", "other", "R", "W", "0",
							   "B", "tornado", "F"]
		self.time_labels = ["current", "future", "I can't tell", "past"]
		self.svm = SVM()
		self.bayes = Bayes()
		self.dt = DecisionTree()
		self.tweet_querier = Query()
		self.tweets = None

	def initialize(self):
		print 'Initializing SVM....'
		self.svm.initialize_svm()
		print 'Done.'
		print 'Initializing Decision Tree....'
		self.dt.initialize_dt()
		print 'Done.'
		print 'Initializing Naive Bayes models....'
		self.bayes.initialize_bayes()
		print 'Done.'
		print 'Loading in tweets....'
		self.load_tweets()
		print 'Loaded Tweets.'
		print 'Initialized classifier.'

	def load_tweets(self):
		cwd = os.getcwd()
		cwd = cwd.split('/')
		if cwd[len(cwd)-1] == 'src':
			data_path = '../data/'
		else:
			data_path = 'data/'
		aggregated_file = data_path + 'twitDB/processed/tweet_data.txt'
		self.tweet_querier.read_data(aggregated_file)

	def classify_with_svm(self, tweet):
		weather_class, time_class = self.svm.classify_tweet(tweet)
		code, conditions = self.get_weather(weather_class)
		return code, conditions

	def classify_with_bayes(self, tweet):
		weather_class, time_class = self.bayes.classify_with_bayes(tweet)
		code, conditions = self.get_weather(weather_class)
		return code, conditions

	def classify_with_dt(self, tweet):
		weather_class, time_class = self.dt.classify_tweet(tweet)
		code, conditions = self.get_weather(weather_class)
		return code, conditions

	def get_weather(self, weather_class):
		labels = []
		for i in range(len(weather_class)):
			weather = weather_class[i]
			if weather > self.threshold:
				labels.append(i)
		code = []
		conditions = []
		for index in labels:
			conditions.append(self.weather_labels[index])
			code.append(self.weather_code[index])
		return code, conditions

