import os
import pdb

import pandas as p
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer


class Parser:

	def __init__(self):
		self.tokenizer = RegexpTokenizer(r'\w+')
		self.stopwords = ["a", "an", "and", "are", "as", "at", "be", "but", "by",
						  "for", "if", "in", "into", "is", "it",
						  "no", "not", "of", "on", "or", "such",
						  "that", "the", "their", "then", "there", "these",
						  "they", "this", "to", "was", "will", "with"]

	def load_data(self, path):
		data = p.read_csv(path)
		return data

	def clean_sentence(self, sentence):
		sentence = sentence.lower()
		sentence = sentence.replace("{link}", "")
		sentence = self.tokenizer.tokenize(sentence)
		cleaned_sentence = []
		for word in sentence:
			if word not in self.stopwords:
				cleaned_sentence.append(word)
		return cleaned_sentence

	def stem_sentence(self, stemmer, sentence):
		sentence = self.clean_sentence(sentence)
		return [stemmer.stem(word) for word in sentence]

	def stem_data(self, stemmer, data):
		print 'Stemming tweets...'
		for i in range(len(data['tweet'])):
			if i%100 == 0:
				print i
			data['tweet'][i] = self.stem_sentence(stemmer, data['tweet'][i])
		return data

	def porter_stem_data(self, data):
		return self.stem_data(PorterStemmer(), data)

	def lancaster_stem_data(self, data):
		return self.stem_data(LancasterStemmer(), data)

	def index_data(self, data):
		index = {}
		index_map = {}
		map_count = 1
		for tweet in data['tweet']:
			for word in tweet:
				try:
					index[word] += 1
				except:
					index[word] = 1
					index_map[word] = map_count
					map_count += 1
		return index, index_map

	def svmlight_format_to_file(self, data, index, index_map, segment=False, segment_size=1000):
		svmlight_temporal_data = ['']*4
		svmlight_weather_data = ['']*15
		multiple = 1

		print 'Converting data to SVMLight format...\n'

		for i in range(len(data['tweet'])): # skip if it is not related to the weather

			if data['s5'][i] < 1:

				tweet = data['tweet'][i]
				entry = ''
				word_list = []
				for word in tweet:
					word_added = False
					for wl in word_list:
						if wl[0] == index_map[word]:
							wl[1] += 1
							word_added = True
							break
					if not word_added:
						word_list.append([index_map[word], 1])
				word_list.sort()
				for word_map, word_count in word_list:
					entry = entry + ' {}:{}'.format(word_map, word_count)
				entry += '\n'

				temporal_labels = []
				for j in range(4): # 4 different temporal data
					temporal_labels.append(data['w{}'.format(j+1)][i])
				max_label_idx = temporal_labels.index(max(temporal_labels))
				for j in range(4):
					if j == max_label_idx:
						labeled_entry = '1'
					else:
						labeled_entry = '-1'
					labeled_entry += entry
					svmlight_temporal_data[j] += labeled_entry

				for j in range(15): # 15 different weather-related features
					if data['k{}'.format(j+1)][i] > 0.7:
						# index is j+4 because we want to access entries after the temporta entries
						labeled_entry = '1'
					else:
						labeled_entry = '-1'
					labeled_entry += entry
					svmlight_weather_data[j] += labeled_entry

			if (i%segment_size == 0 and i) > 0 or i == len(data['tweet']):
				print 'Converted {} of {}'.format(i, len(data['tweet']))
				idx = 1
				for d in svmlight_temporal_data:
					if segment:
						filename = 'w{}_{}.train'.format(idx, multiple)
					else:
						filename = 'w{}.train'.format(idx)
					f = open(filename, 'a')
					f.write(d)
					f.close()
					idx += 1
				idx = 1
				for d in svmlight_weather_data:
					if segment:
						filename = 'k{}_{}.train'.format(idx, multiple)
					else:
						filename = 'k{}.train'.format(idx)
					f = open(filename, 'a')
					f.write(d)
					f.close()
					idx += 1
				svmlight_temporal_data = ['']*4
				svmlight_weather_data = ['']*15
				multiple += 1


# parser = Parser()
# data = parser.load_data('../data/train.csv')
# data = parser.porter_stem_data(data)
# index, index_map = parser.index_data(data)
# svm_data = parser.svmlight_format_to_file(data, index, index_map)
# svm_data = parser.svmlight_format_to_file(data, index, index_map, segment=True, segment_size=7000)







