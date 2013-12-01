import os
import pdb
import math
import numpy as np
import svmlight_loader as svml

class BinaryNaiveBayes():

	def __init__(self, feature, vocab_size, positive_y, negative_y, positive_x, negative_x):
		self.feature = feature 							# string... (ex) 'k1' 'w1'
		self.vocab_size = vocab_size

		self.total = float(len(positive_y) + len(negative_y))
		self.positive_y = float(len(positive_y)) 			# (Y = +1)
		self.negative_y = float(len(negative_y))			# (Y = -1)

		self.positive_x = positive_x					# (X = xi | Y = +1)
		self.negative_x = negative_x					# (X = xi | Y = -1)
		self.positive_sum = float(sum(positive_x.values()))
		self.negative_sum = float(sum(negative_x.values()))

	def get_feature(self):
		return self.feature

	def classify(self, example):
		positive_score = self.score(example, True)
		negative_score = self.score(example, False)
		return (positive_score - negative_score) / (abs(positive_score) + abs(negative_score))

	def score(self, example, positive):
		py, px, tw = None, None, None
		if positive:
			py = self.positive_y / self.total
			px = self.positive_x
			tw = self.positive_sum
		else:
			py = self.negative_y / self.total
			px = self.negative_x
			tw = self.negative_sum

		s = math.log(py)
		for e in example:
			if e in px:
				s += math.log(float(1+px[e]) / float(self.vocab_size+tw))
		return s

class MultiBinaryNaiveBayes():

	def __init__(self, features, vocab_size, positive_ys, negative_ys, positive_xs, negative_xs):
		self.nb = {}
		for idx, f in enumerate(features):
			self.nb[f] = BinaryNaiveBayes(f, vocab_size, positive_ys[idx], negative_ys[idx], positive_xs[idx], negative_xs[idx])

	def classify(self, example):
		result = []
		for f in self.nb:
			classifier = self.nb[f]
			s = classifier.classify(example)
			result.append((f,s))
		return result

class MultinomialNaiveBayes():

	def __init__(self, features, vocab_size, ys, xs):
		self.vocab_size = vocab_size
		self.features = features
		self.total = 0
		self.y_length = {}
		self.x_length = {}
		self.xs = xs
		self.ys = ys
		for f in features:
			self.x_length[f] = float(sum(xs[f].values()))
			self.y_length[f] = float(len(ys[f]))
			self.total += self.y_length[f]

	def classify(self, example):
		result = []
		for f in self.features:
			py = self.y_length[f] / self.total
			tw = self.x_length[f]
			px = self.xs[f]
			s = self.score(example, px, py, tw)
			result.append((f, s))
		return result

	def score(self, example, px, py, tw):
		s = math.log(py)
		for e in example:
			if e in px:
				s += math.log(float(1+px[e]) / float(self.vocab_size+tw))
		return s





