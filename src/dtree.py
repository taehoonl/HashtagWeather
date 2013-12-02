import os
import pdb
from math import log, ceil
from operator import itemgetter
import pickle
import time

import numpy as np

from parser import Parser


class Node:
	def __init__(self, left=None, right=None, criterion=None, label=None, depth=None):
		# in our case, it is on whether the document has a word -- a string
		self.criterion = criterion
		self.left = left
		self.right = right
		self.label = label
		self.depth = depth
		self.parser = None

	def get_label(self, tweet, tweet_cleaned=False):
		if self.parser is None:
			self.parser = Parser()
		if not tweet_cleaned:
			# tweet = self.parser.stem_sentence_porter(tweet)
			tweet_cleaned = True
		if self.criterion:
			print self.criterion
			if self.criterion in tweet:
				# if has, go right, else left
				return self.right.get_label(tweet, tweet_cleaned)
			else:
				return self.left.get_label(tweet, tweet_cleaned)
		return self.label

class DecisionTree:

	def __init__(self):
		self.root = None
		self.keys = None
		self.parser = Parser()

	def create_decision_tree_for_k(self, pos_data, neg_data, depth, attr, max_depth=None):
		'''
		Trains and returns a decision tree with the information gain
		as the tree splitting criterion. Criterion is a binary function
		which checks to see if a word exists in the tweet or not
		'''

		root = Node(depth=depth)

		if self.root is None:
			self.root = root

		if depth == max_depth:
			if len(pos_data) > len(neg_data):
				root.label = 1
				return root
			else:
				root.label = -1
				return root

		if len(pos_data) == 0:
			root.label = -1
			return root
		elif len(neg_data) == 0:
			root.label = 1
			return root

		print 'Current depth: {}'.format(depth)
		criterion_word = self.max_gain(pos_data, neg_data)
		root.criterion = criterion_word

		# cps = set positive tweets that contain the word
		# cns = set negative tweets that contain the word
		# ncps = set positive tweets that do not contain the word
		# ncns = set negative tweets that do not contain the word
		cps, ncps, cns, ncns = self.split_on_word(pos_data, neg_data, criterion_word)

		if criterion_word == 'rain':
			print 'Contains: {}, {}'.format(cps, cns)
			print 'Not Contains: {}, {}'.format(ncps, ncns)

		root.left = self.create_decision_tree_for_k(ncps, ncns, depth+1, attr, max_depth=max_depth)
		root.right = self.create_decision_tree_for_k(cps, cns, depth+1, attr, max_depth=max_depth)
		return root

	def entropy(self, pos_data, neg_data):
		'''
		Calculates and returns the entropy of S (S=labels) with the
		formula:
		Entropy(S) = -p_pos*log2(p_pos)-p_neg*log2(p_neg)
		'''
		if len(data) == 0:
			return 0
		else:
			tot = float(len(pos_data) + len(neg_data))

		pos = len(pos_data)
		if pos == 0:
			pos = tot
		neg = tot-pos
		if neg == 0:
			neg = tot
		if tot == 0:
			return 0
		return -(pos/tot)*log(pos/tot,2)-(neg/tot)*log(neg/tot,2)


	def gain(self, pos_data, neg_data, word):
		'''
		Calculates and returns the Gain(S,A) of an attribute A, with
		relative to a collection of examples S
		'''
		set_entropy = self.entropy(pos_data, neg_data)
		contains_pos_set, not_contains_pos_set, contains_neg_set, not_contains_neg_set = self.split_on_word(pos_data, neg_data, word)

		len_contains = float(len(contains_pos_set) + len(contains_neg_set))
		len_not_contains = float(len(not_contains_pos_set) + len(not_contains_neg_set))

		contains_subset_entropy = self.entropy(contains_pos_set, contains_neg_set)*len_contains/(len_contains+len_not_contains)
		not_contains_subset_entropy = self.entropy(not_contains_pos_set, not_contains_neg_set)*len_not_contains/(len_contains+len_not_contains)
		subset_entropy = contains_subset_entropy + not_contains_subset_entropy
		return set_entropy-subset_entropy


	def max_gain(self, pos_data, neg_data):
		max_gain = 0
		max_word = None
		count = 0
		for key in self.keys:
			gain = self.gain(pos_data, neg_data, key)
			if gain > max_gain:
				max_gain = gain
				max_word = key
		return max_word

	def split_on_word(self, pos_data, neg_data, word):
		contains_pos_set = []
		not_contains_pos_set = []
		contains_neg_set = []
		not_contains_neg_set = []

		for i in range(len(pos_data)):
			if word in pos_data[i][1]:
				contains_pos_set.append(pos_data[i])
			else:
				not_contains_pos_set.append(pos_data[i])
		for i in range(len(neg_data)):
			if word in neg_data[i][1]:
				contains_neg_set.append(neg_data[i])
			else:
				not_contains_neg_set.append(neg_data[i])
		return contains_pos_set, not_contains_pos_set, contains_neg_set, not_contains_neg_set

	def validate(self, tree, pos_data, neg_data):
		correct = 0
		wrong = 0
		for datum in pos_data:
			tweet = datum[1]
			label = tree.get_label(tweet, tweet_cleaned=True)
			if label == 1:
				correct += 1
			else:
				wrong += 1
		for datum in neg_data:
			tweet = datum[1]
			label = tree.get_label(tweet, tweet_cleaned=True)
			if label == 1:
				wrong += 1
			else:
				correct += 1
		accuracy = float(correct)/(correct+wrong)
		print "Accuracy of tree is: {}".format(accuracy)

	def load_tree(self, filename):
		f = open(filename, 'r')
		dt = pickle.load(f)
		return dt

# tree = DecisionTree()
# data = tree.parser.load_data('../data/train_tree.csv')
# data = tree.parser.porter_stem_data(data)
# index, index_map = tree.parser.index_data(data)
# keys = index.keys()
# for key in keys:
# 	if index[key] == 1:
# 		keys.remove(key)
# 	try:
# 		number = int(key)
# 		keys.remove(key)
# 	except:
# 		pass
# tree.keys = keys
# # for i in range(4):
# # 	pos_data, neg_data = tree.parser.get_label_divided_data(data, 'w{}'.format(i+1))
# # 	dt = tree.create_decision_tree_for_k(pos_data, neg_data, depth=1, attr='w{}'.format(i+1), max_depth=15)
# # 	filename = 'dt_w{}.tree'.format(i+1)
# # 	f = open(filename, 'w')
# # 	pickle.dump(dt, f)
# for i in range(12,15):
# 	pos_data, neg_data = tree.parser.get_label_divided_data(data, 'k{}'.format(i+1))
# 	dt = tree.create_decision_tree_for_k(pos_data, neg_data, depth=1, attr='k{}'.format(i+1), max_depth=15)
# 	filename = 'dt_k{}.tree'.format(i+1)
# 	f = open(filename, 'w')
# 	pickle.dump(dt, f)
# pdb.set_trace()


