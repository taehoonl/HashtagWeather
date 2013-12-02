import os
import pdb
import math
import numpy as np
import svmlight_loader as svml
from parser import Parser

class NaiveBayes():

	def __init__(self, feature, vocab_size, positive_y, negative_y, positive_x, negative_x):
		self.parser = Parser()
		self.feature = feature 							# string... (ex) 'k1' 'w1'
		self.vocab_size = vocab_size

		self.total = float(len(positive_y) + len(negative_y))
		self.positive_y = float(len(positive_y)) 			# (Y = +1)
		self.negative_y = float(len(negative_y))			# (Y = -1)

		self.positive_x = positive_x					# (X = xi | Y = +1)
		self.negative_x = negative_x					# (X = xi | Y = -1)
		self.positive_sum = float(sum(positive_x.values()))
		self.negative_sum = float(sum(negative_x.values()))

	def classify(self, example):
		e = example
		if type(example) is str:
			e = self.parser.stem_sentence_porter(example)
		elif type(example) is list:
			pass
		else:
			print "example should be of type str or list of str"
		positive_score = self.score(e, True)
		negative_score = self.score(e, False)
		return -1.0*(positive_score - negative_score)#/ (abs(positive_score) + abs(negative_score))

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
		# s = py
		for e in example:
			if e in px:
				# s *= float(px[e])/float(tw)
				# s += math.log(float(px[e])/float(tw))
				s += math.log(float(1+px[e]) / float(self.vocab_size+tw))
		return s

class MultiNaiveBayes():

	def __init__(self, features, vocab_size, positive_ys, negative_ys, positive_xs, negative_xs):
		self.features = features
		self.nb = {}
		for idx, f in enumerate(features):
			self.nb[f] = NaiveBayes(f, vocab_size, positive_ys[idx], negative_ys[idx], positive_xs[idx], negative_xs[idx])

	def classify_multi(self, example):
		result = []
		for f in self.features:
			classifier = self.nb[f]
			s = classifier.classify(example)
			result.append((f,s))
		return result

	def classify_top(self, example):
		w = self.classify_multi(example)
		w_sorted = sorted(w, key=lambda (a,b): b)
		top, dontcare = w_sorted[len(self.features)-1]
		return top

	def classify_all(self, example, threshold):
		result = [-1] * len(self.features)
		w_dict = {}
		w = self.classify_multi(example)
		for (k,v) in w:
			w_dict[k] = v

		for i, f in enumerate(self.features):
			if w_dict[f] > threshold:
				result[i] = 1
		return result

# class MultinomialNaiveBayes():

# 	def __init__(self, features, vocab_size, ys, xs):
# 		self.vocab_size = vocab_size
# 		self.features = features
# 		self.total = 0
# 		self.y_length = {}
# 		self.x_length = {}
# 		self.xs = xs
# 		self.ys = ys
# 		for f in features:
# 			self.x_length[f] = float(sum(xs[f].values()))
# 			self.y_length[f] = float(len(ys[f]))
# 			self.total += self.y_length[f]

# 	def classify(self, example):
# 		result = []
# 		for f in self.features:
# 			py = self.y_length[f] / self.total
# 			tw = self.x_length[f]
# 			px = self.xs[f]
# 			s = self.score(example, px, py, tw)
# 			result.append((f, s))
# 		return result

# 	def score(self, example, px, py, tw):
# 		s = math.log(py)
# 		for e in example:
# 			if e in px:
# 				s += math.log(float(1+px[e]) / float(self.vocab_size+tw))
# 		return s





