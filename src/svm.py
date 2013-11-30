import os
import pdb

import numpy as np
import svmlight
import svmlight_loader as svml

class SVM:

	def __init__(self):
		pass

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
				data_features[e] = (e+1, datum[1][e])

			if data_num%100 == 0:
				print 'Formatted {} data'.format(data_num)
			data_num += 1
			formatted_data.append((datum[0], data_features))
		return formatted_data

	def format_for_svmlight(self, data):
		combined_data = self.combine_data(data)
		formatted_data = self.format_data(combined_data)
		return formatted_data

	def data_labels_to_tuple(data, target_label):
		tuple_data = []
		for datum in data:
			if datum[0] == target_label:
				tuple_data.append((1, datum[1]))
			else:
				tuple_data.append((-1, datum[1]))
		return tuple_data

	def train(self, data, t=0, C=1.0):
		model = svmlight.learn(data, type="classifier", t=t, C=C)
		return model

	def classify(self, model, data):
		classifications = svmlight.classify(model, data)
		return classifications

	def read_model(self, rel_path):
		abs_path = os.path.abspath(rel_path)
		model = svmlight.read_model(abs_path)
		return model









