import os
import pdb

import numpy as np
import svmlight
import svmlight_loader as svml

from parser import Parser
from svm import SVM
from naivebayes import *

# global 
threshold = 0.7



def svm_classify():
	svm = SVM()
	classifications = []
	temporal_labels = []
	for i in range(4):
		model_name = 'w{}.model'.format(i+1)
		data_name = 'w{}_1.train'.format(i+1)
		model = svm.read_model('../data/svm/models/{}'.format(model_name))
		data = svm.load_data('../data/svm/train_seg/{}'.format(data_name))
		temporal_labels.append(data[1])
		data = svm.format_for_svmlight(data)
		print 'Classifying temporal data...'
		classifications.append(svm.classify(model, data))
		print 'Finished classifying.'

	temporal_classifications = []
	for j in range(len(classifications[0])):
		class_list = []
		for k in range(len(classifications)):
			class_list.append(classifications[k][j])
		max_attr = max(class_list)
		labels = [-1.0]*len(classifications)
		labels[class_list.index(max_attr)] = 1.0
		temporal_classifications.append(labels)

	classifications = []
	weather_labels = []
	for i in range(14):
		model_name = 'k{}.model'.format(i+1)
		data_name = 'k{}_1.train'.format(i+1)
		model = svm.read_model('../data/svm/models/{}'.format(model_name))
		data = svm.load_data('../data/svm/train_seg/{}'.format(data_name))
		weather_labels.append(data[1])
		data = svm.format_for_svmlight(data)
		print 'Classifying weather data...'
		classifications.append(svm.classify(model, data))
		print 'Finished classifying.'

	weather_classifications = []
	for j in range(len(classifications[0])):
		class_list = []
		for k in range(len(classifications)):
			class_list.append(classifications[k][j])
		max_attr = max(class_list)
		labels = [-1.0]*len(classifications)
		labels[class_list.index(max_attr)] = 1.0
		weather_classifications.append(labels)

	t_correct = 0
	t_incorrect = 0
	for j in range(len(temporal_classifications)):
		for k in range(len(temporal_labels)):
			if temporal_classifications[j][k] == temporal_labels[k][j]:
				t_correct += 1
			else:
				t_incorrect += 1

	w_correct = 0
	w_incorrect = 0
	for j in range(len(weather_classifications)):
		for k in range(len(weather_labels)):
			if weather_classifications[j][k] == weather_labels[k][j]:
				w_correct += 1
			else:
				w_incorrect += 1

	t_accuracy = float(t_correct)/(t_correct + t_incorrect)
	print 'Accuracy for temporal data is: {}'.format(t_accuracy)
	w_accuracy = float(w_correct)/(w_correct + w_incorrect)
	print 'Accuracy for weather data is: {}'.format(w_accuracy)
	pdb.set_trace()

def bayes_classify():
	time_label_keys = ['w1', 'w2', 'w3', 'w4']
	weather_label_keys = ['k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7',
						'k8', 'k9', 'k10', 'k11', 'k12', 'k13', 'k14', 'k15']

	parser = Parser()
	data = parser.load_data('../data/train.csv')
	data = parser.porter_stem_data(data)
	index, index_map = parser.index_data(data)
	vocab_size = sum(index.values())

	# temporal labels
	temporal_classifications = []
	temporal_labels = []
	for i in range(len(data['id'])):
		w = []
		for f in time_label_keys:
			w.append((f, data[f][i]))
		w_sorted = sorted(w, key=lambda temp: temp[1])
		top, dontcare = w_sorted[3]
		temporal_labels.append(top)

	# weather labels
	weather_classifications = []
	weather_labels = []
	for i in range(len(data['id'])):
		w = [-1] * len(weather_label_keys)
		for idx, f in enumerate(weather_label_keys):
			if data[f][i] > threshold:
				w[idx] = 1
		weather_labels.append(w)


	'''
	using MultiBinaryNaiveBayes
	'''
	time_positive_ys = []
	time_negative_ys = []
	time_positive_xs = []
	time_negative_xs = []
	for f in time_label_keys:
		pos, neg = parser.get_label_divided_data(data, f)
		time_positive_ys.append(pos)
		time_negative_ys.append(neg)

		pos_index, pos_idx_map = parser.labeled_index_data(data, pos)
		time_positive_xs.append(pos_index)

		neg_index, neg_idx_map = parser.labeled_index_data(data, neg)
		time_negative_xs.append(neg_index)

	time_nb = MultiBinaryNaiveBayes(time_label_keys, vocab_size, time_positive_ys, time_negative_ys, time_positive_xs, time_negative_xs)
	print "finished training for w[1-4] naive bayes classifier"

	# classify temporal
	tweets = data['tweet']
	for t in tweets:
		w = time_nb.classify(t)
		w_sorted = sorted(w, key=lambda (a,b): b)
		top, dontcare = w_sorted[3]
		temporal_classifications.append(top)

	# accuracy (binary approach = 0.59)
	correct = 0
	total = 0
	for i in range(len(temporal_classifications)):
		total += 1
		if temporal_classifications[i] == temporal_labels[i]:
			correct += 1
	print "time accurracy : " + str(float(correct)/float(total))
	# pdb.set_trace()

	weather_positive_ys = []
	weather_negative_ys = []
	weather_positive_xs = []
	weather_negative_xs = []
	for f in weather_label_keys:
		pos, neg = parser.get_label_divided_data(data, f)
		weather_positive_ys.append(pos)
		weather_negative_ys.append(neg)

		pos_index, pos_idx_map = parser.labeled_index_data(data, pos)
		weather_positive_xs.append(pos_index)

		neg_index, neg_idx_map = parser.labeled_index_data(data, neg)
		weather_negative_xs.append(neg_index)

	weather_nb = MultiBinaryNaiveBayes(weather_label_keys, vocab_size, weather_positive_ys, weather_negative_ys, weather_positive_xs, weather_negative_xs)
	print "finished training for k[1-15] naive bayes classifier"

	# classify weather
	tweets = data['tweet']
	for t in tweets:
		result = [-1] * len(weather_label_keys)
		w_dict = {}
		w = weather_nb.classify(t)
		for (k,v) in w:
			w_dict[k] = v

		for i, f in enumerate(weather_label_keys):
			if w_dict[f] > threshold:
				result[i] = 1
		weather_classifications.append(result)

	# accuracy ()
	correct = [0] * len(weather_label_keys)
	total = 0
	for i in range(len(weather_classifications)):
		total += 1
		for k in range(len(weather_label_keys)):
			if int(weather_classifications[i][k]) == int(weather_labels[i][k]):
				correct[k] += 1

	for i in range(len(weather_label_keys)):
		print weather_label_keys[i] + " accuracy : " + str(float(correct[i])/ float(total)) 

	pdb.set_trace()

	'''
	using MultinomialNaiveBayes
	'''
	# time_data = parser.divide_data(data, 'w')
	# time_xs = {}
	# for f in time_label_keys:
	# 	index_data, index_map = parser.labeled_index_data(data, time_data[f])
	# 	time_xs[f] = index_data

	# time_mnb = MultinomialNaiveBayes(time_label_keys, vocab_size, time_data, time_xs)

	# # training tweets
	# tweets = data['tweet']
	# for t in tweets:
	# 	w = time_mnb.classify(t)
	# 	w_sorted = sorted(w, key=lambda temp: temp[1])
	# 	top, dontcare = w_sorted[3]
	# 	temporal_classifications.append(top)

	# # accuracy (non-binary = 0.56)
	# correct = 0
	# total = 0
	# for i in range(len(temporal_classifications)):
	# 	total += 1
	# 	if temporal_classifications[i] == temporal_labels[i]:
	# 		correct += 1

	# pdb.set_trace()


# svm_classify()
bayes_classify()