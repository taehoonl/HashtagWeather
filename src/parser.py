import os
import pdb

import pandas as p
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer


class Parser:

	def __init__(self, threshold=0.7):
		self.tokenizer = RegexpTokenizer(r'\w+')
		self.stopwords = ["a", "an", "and", "are", "as", "at", "be", "but", "by",
						  "for", "if", "in", "into", "is", "it",
						  "no", "not", "of", "on", "or", "such",
						  "that", "the", "their", "then", "there", "these",
						  "they", "this", "to", "was", "will", "with"]
		self.threshold = threshold

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

	def stem_sentence_porter(self, sentence):
		return self.stem_sentence(PorterStemmer(), sentence)

	def stem_data(self, stemmer, data):
		print 'Stemming tweets...'
		for i in range(len(data['tweet'])):
			if i%1000 == 0:
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

	def labeled_index_data(self, data, labeled_data):
		index = {}
		index_map = {}
		map_count = 1
		# pdb.set_trace()
		for tweet_id, tweet in labeled_data:
			for word in tweet:
				try:
					index[word] += 1
				except:
					index[word] = 1
					index_map[word] = map_count
					map_count += 1
		return index, index_map

	def get_label_divided_data(self, data, label_key):
		pos_data = []
		neg_data = []
		time_label_keys = ['w1', 'w2', 'w3', 'w4']
		weather_label_keys = ['k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7',
							  'k8', 'k9', 'k10', 'k11', 'k12', 'k13', 'k14', 'k15']
		if label_key in time_label_keys:
			key_num = int(label_key[1])
			for i in range(len(data['w1'])):
				t_labels = []
				for j in range(4): # 4 different temporal data
					t_labels.append(data['w{}'.format(j+1)][i])
				max_label_idx = t_labels.index(max(t_labels))
				if key_num == max_label_idx+1:
					pos_data.append([data['id'][i], data['tweet'][i]])
				else:
					neg_data.append([data['id'][i], data['tweet'][i]])
			return pos_data, neg_data

		elif label_key in weather_label_keys:
			for i in range(len(data['w1'])):
				if data[label_key][i] > self.threshold:
					pos_data.append([data['id'][i], data['tweet'][i]])
				else:
					neg_data.append([data['id'][i], data['tweet'][i]])
			return pos_data, neg_data
		else:
			return None

	def divide_data(self, data, wk):
		result = {}
		time_label_keys = ['w1', 'w2', 'w3', 'w4']
		weather_label_keys = ['k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7',
							  'k8', 'k9', 'k10', 'k11', 'k12', 'k13', 'k14', 'k15']

		if wk is 'w':
			for k in time_label_keys:
				result[k] = []

			for i in range(len(data['id'])):
				list_temp = []
				for l in time_label_keys:
					list_temp.append((l, data[l][i]))
				list_sorted = sorted(list_temp, key=lambda temp: temp[1])
				top, dontcare = list_sorted[len(time_label_keys)-1]
				result[top].append([data['id'][i], data['tweet'][i]])

		elif wk is 'k':
			for k in weather_label_keys:
				result[k] = []

			for i in range(len(data['id'])):
				for l in weather_label_keys:
					if data[l][i] > self.threshold:
						result[l].append([data['id'][i], data['tweet'][i]])

		else:
			print "enter either w or k"
			return None

		return result


	def svmlight_format_to_file(self, data, index, index_map, segment=False, segment_size=1000):
		svmlight_temporal_data = ['']*4
		svmlight_weather_data = ['']*15
		multiple = 1

		pdb.set_trace()

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

			if (i%segment_size == 0 and i) > 0 or i == len(data['tweet'])-1:
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
# pos, neg = parser.get_label_divided_data(data, 'w1')
# pos_index, idx_map = parser.labeled_index_data(data, pos)
# pdb.set_trace()
# index, index_map = parser.index_data(data)
# svm_data = parser.svmlight_format_to_file(data, index, index_map)
# svm_data = parser.svmlight_format_to_file(data, index, index_map, segment=True, segment_size=10000)







