import os
import pdb
from math import log, ceil
from operator import itemgetter

import numpy as np


class Node:
	def __init__(self, left=None, right=None,
				 data=None, criterion=None, label=None, depth=None):
		# in our case, it is on whether the document has a word -- a string
		self.criterion = criterion
		self.left = left
		self.right = right
		self.data = data
		self.label = label
		self.depth = depth

	def get_label(self, tweet):
		if self.criterion:
			if self.criterion in tweet:
				# if has, go right, else left
				return self.left.get_point_label(tweet)
			else:
				return self.right.get_point_label(tweet)
		return self.label

class DecisionTree:

	def __init__(self, root=None):
		self.root = root

	def decision_tree(data, depth):
		'''
		Trains and returns a decision tree with the information gain
		as the tree splitting criterion. Criterion is a binary function
		which checks to see if a word exists in the tweet or not
		'''
		root = Node(depth=depth)
		data_len = len(data)

		# some hack
		dd = data[:]
		dd.sort(key=itemgetter(1), reverse=True)

		num_positive = np.sum(data, axis=0)[1]
		if data_len == num_positive:
			root.label = 1
			return root
		elif num_positive == 0:
			root.label = -1
			return root
		elif ceil(dd[0][0][0])-ceil(dd[data_len-1][0][0]) == 0:
			if ceil(dd[0][0][1])-ceil(dd[data_len-1][0][1]) == 0:
				if dd[0][1]-dd[data_len-1][1] != 0.0:
					root.label = 1
					return root

		max_gain_info = max_gain(data)
		root.criterion = max_gain_info
		data_subset_1 = []
		data_subset_2 = []
		for i in range(data_len):
			if data[i][0][max_gain_info[0]] >= max_gain_info[1]:
				data_subset_1.append(data[i])
			else:
				data_subset_2.append(data[i])
		root.left = decision_tree(data_subset_1, depth=depth+1)
		root.right = decision_tree(data_subset_2, depth=depth+1)
		return root

	def entropy(data):
		'''
		Calculates and returns the entropy of S (S=labels) with the
		formula:
		Entropy(S) = -p_pos*log2(p_pos)-p_neg*log2(p_neg)
		'''
		if len(data) == 0:
			return 0
		else:
			tot = float(len(data))

		num_positive = np.sum(data, axis=0)[1]
		pos = num_positive
		if pos == 0:
			pos = tot
		neg = tot-num_positive
		if neg == 0:
			neg = tot
		return -(pos/tot)*log(pos/tot,2)-(neg/tot)*log(neg/tot,2)


	def gain(data, target_attr, attr_val):
		'''
		Calculates and returns the Gain(S,A) of an attribute A, with
		relative to a collection of examples S
		'''
		subset_entropy = 0
		data_subset_1 = [datum for datum in data if datum[0][target_attr] >= attr_val]
		data_subset_2 = [datum for datum in data if datum[0][target_attr] < attr_val]
		subset_entropy = (float(len(data_subset_1))/len(data))*entropy(data_subset_1)
		subset_entropy += (float(len(data_subset_2))/len(data))*entropy(data_subset_2)
		return entropy(data)-subset_entropy


	def max_gain(data):
		max_gain_val = 0
		max_gain_idx = [0,0]
		for target_attr in range(len(data[0])):
			for attr in range(10):
				gain_val = gain(data, target_attr, attr)
				if gain_val > max_gain_val:
					max_gain_val = gain_val
					max_gain_idx = [target_attr, attr]
		return max_gain_idx


