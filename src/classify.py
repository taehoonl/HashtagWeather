import os
import pdb

import numpy as np
import svmlight
import svmlight_loader as svml

from parser import Parser
from svm import SVM

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


svm_classify()