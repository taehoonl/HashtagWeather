import pickle
import pdb

w_nb = None
k_nb = None
threshold = 0.9

def unpickle_obj(filename):
	f = open(filename, "r")
	obj = pickle.load(f)
	f.close()
	return obj

def initialize_bayes():
	global w_nb, k_nb
	w_nb = unpickle_obj('../data/bayes_model/time_nb.obj')
	k_nb = unpickle_obj('../data/bayes_model/weather_nb.obj')

def classify_with_bayes(tweet):
	global w_nb, k_nb, threshold
	time_result = w_nb.classify_top(tweet)
	weather_result = k_nb.classify_all(tweet, threshold)
	return time_result, weather_result


initialize_bayes()
pdb.set_trace()
	
		

