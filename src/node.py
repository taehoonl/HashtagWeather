import os
import pdb
import pickle

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
			tweet = self.parser.stem_sentence_porter(tweet)
			tweet_cleaned = True
		if self.criterion:
			if self.criterion in tweet:
				# if has, go right, else left
				return self.right.get_label(tweet, tweet_cleaned)
			else:
				return self.left.get_label(tweet, tweet_cleaned)
		return self.label