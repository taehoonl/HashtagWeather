import os
import pdb

import numpy as np
import pickle
import svmlight
import svmlight_loader as svml

from parser import Parser
from svm import SVM
from naivebayes import *

# global 
threshold = 0.9

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

	parser2 = Parser()
	validation_data = parser2.load_data('../data/validation.csv')
	validation_data = parser2.porter_stem_data(validation_data)
	# validation_index, validation_index_map = parser2.index_data(validation_data)

	# temporal labels
	temporal_classifications = []
	temporal_labels = []
	for i in range(len(validation_data['id'])):
		w = []
		for f in time_label_keys:
			w.append((f, validation_data[f][i]))
		w_sorted = sorted(w, key=lambda temp: temp[1])
		top, dontcare = w_sorted[3]
		temporal_labels.append(top)

	# weather labels
	weather_classifications = []
	weather_labels = []
	for i in range(len(validation_data['id'])):
		w = [-1] * len(weather_label_keys)
		for idx, f in enumerate(weather_label_keys):
			if validation_data[f][i] > threshold:
				w[idx] = 1
		weather_labels.append(w)


	'''
	using MultiNaiveBayes
	'''
	time_positive_ys = []
	time_negative_ys = []
	time_positive_xs = []
	time_negative_xs = []
	for f in time_label_keys:
		pos, neg = parser.get_label_divided_data(validation_data, f)
		time_positive_ys.append(pos)
		time_negative_ys.append(neg)

		pos_index, pos_idx_map = parser.labeled_index_data(validation_data, pos)
		time_positive_xs.append(pos_index)

		neg_index, neg_idx_map = parser.labeled_index_data(validation_data, neg)
		time_negative_xs.append(neg_index)

	time_nb = MultiNaiveBayes(time_label_keys, vocab_size, time_positive_ys, time_negative_ys, time_positive_xs, time_negative_xs)
	print "finished training for w[1-4] naive bayes classifier"

	# classify temporal
	tweets = validation_data['tweet']
	for t in tweets:
		# w = time_nb.classify(t)
		# w_sorted = sorted(w, key=lambda (a,b): b)
		# top, dontcare = w_sorted[3]
		top = time_nb.classify_top(t)
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
		pos, neg = parser.get_label_divided_data(validation_data, f)
		weather_positive_ys.append(pos)
		weather_negative_ys.append(neg)

		pos_index, pos_idx_map = parser.labeled_index_data(validation_data, pos)
		weather_positive_xs.append(pos_index)

		neg_index, neg_idx_map = parser.labeled_index_data(validation_data, neg)
		weather_negative_xs.append(neg_index)

	weather_nb = MultiNaiveBayes(weather_label_keys, vocab_size, weather_positive_ys, weather_negative_ys, weather_positive_xs, weather_negative_xs)
	print "finished training for k[1-15] naive bayes classifier"

	# classify weather
	tweets = validation_data['tweet']
	for t in tweets:
		# result = [-1] * len(weather_label_keys)
		# w_dict = {}
		# w = weather_nb.classify(t)
		# for (k,v) in w:
		# 	w_dict[k] = v

		# for i, f in enumerate(weather_label_keys):
		# 	if w_dict[f] > threshold:
		# 		result[i] = 1
		result = weather_nb.classify_all(t, threshold)
		weather_classifications.append(result)

	# accuracy ()
	correct = [0] * len(weather_label_keys)
	total = 0
	for i in range(len(weather_classifications)):
		total += 1
		for k in range(len(weather_label_keys)):
			if int(weather_classifications[i][k]) == int(weather_labels[i][k]):
				correct[k] += 1

	acc = 0.0
	for i in range(len(weather_label_keys)):
		print weather_label_keys[i] + " accuracy : " + str(float(correct[i])/ float(total)) 
		acc += float(correct[i])/ float(total)

	print "weather accuracy : {}".format(acc/float(len(weather_label_keys)))
	print "threshold : {}".format(threshold)
	pdb.set_trace()	

	'''
	write object files for classifiers
	'''
	


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

'''
Multinomial Bayes result

threshold : 0.1
time accurracy : 0.494077400043
weather accuracy : 0.636014539235
k1 accuracy : 0.747316655976
k2 accuracy : 0.714646140688
k3 accuracy : 0.48300192431
k4 accuracy : 0.691768227496
k5 accuracy : 0.726149240966
k6 accuracy : 0.16805644644
k7 accuracy : 0.544408809066
k8 accuracy : 0.353944836434
k9 accuracy : 0.628864656831
k10 accuracy : 0.765191361984
k11 accuracy : 0.802822322001
k12 accuracy : 0.751336326705
k13 accuracy : 0.687363694676
k14 accuracy : 0.707804147958
k15 accuracy : 0.767543296985


threshold : 0.2
time accurracy : 0.494077400043
weather accuracy : 0.742188012259
k1 accuracy : 0.855377378662
k2 accuracy : 0.804618345093
k3 accuracy : 0.668163352576
k4 accuracy : 0.781526619628
k5 accuracy : 0.839255933291
k6 accuracy : 0.294419499679
k7 accuracy : 0.612999786188
k8 accuracy : 0.521744708146
k9 accuracy : 0.748770579431
k10 accuracy : 0.834723113107
k11 accuracy : 0.89339320077
k12 accuracy : 0.804575582638
k13 accuracy : 0.771349155442
k14 accuracy : 0.846440025657
k15 accuracy : 0.855462903571

threshold : 0.3
weather accuracy : 0.81780058442
time accurracy : 0.494077400043
k1 accuracy : 0.923412443874
k2 accuracy : 0.859910198845
k3 accuracy : 0.816720119735
k4 accuracy : 0.837802009835
k5 accuracy : 0.900577293137
k6 accuracy : 0.442420354928
k7 accuracy : 0.66632456703
k8 accuracy : 0.667564678213
k9 accuracy : 0.87765661749
k10 accuracy : 0.867051528758
k11 accuracy : 0.933547145606
k12 accuracy : 0.830318580287
k13 accuracy : 0.826598246739
k14 accuracy : 0.915287577507
k15 accuracy : 0.901817404319

threshold : 0.4
weather accuracy : 0.861309956525
time accurracy : 0.494077400043
k1 accuracy : 0.954800085525
k2 accuracy : 0.882018387855
k3 accuracy : 0.908445584777
k4 accuracy : 0.862091084028
k5 accuracy : 0.93508659397
k6 accuracy : 0.583921317084
k7 accuracy : 0.697070771862
k8 accuracy : 0.772974128715
k9 accuracy : 0.929826812059
k10 accuracy : 0.882232200128
k11 accuracy : 0.949967928159
k12 accuracy : 0.840153944836
k13 accuracy : 0.844130853111
k14 accuracy : 0.951892238614
k15 accuracy : 0.925037417148


threshold : 0.5
weather accuracy : 0.891568669375
time accurracy : 0.494077400043
k1 accuracy : 0.971092580714
k2 accuracy : 0.897241821681
k3 accuracy : 0.95672439598
k4 accuracy : 0.882488774856
k5 accuracy : 0.953645499252
k6 accuracy : 0.709471883686
k7 accuracy : 0.724738079966
k8 accuracy : 0.847637374385
k9 accuracy : 0.967201197349
k10 accuracy : 0.891982039769
k11 accuracy : 0.957836219799
k12 accuracy : 0.848321573658
k13 accuracy : 0.85704511439
k14 accuracy : 0.968013683985
k15 accuracy : 0.940089801155

threshold : 0.6
time accurracy : 0.494077400043
weather accuracy : 0.912753189366
k1 accuracy : 0.979773358991
k2 accuracy : 0.907333760958
k3 accuracy : 0.980842420355
k4 accuracy : 0.893820825315
k5 accuracy : 0.967757109258
k6 accuracy : 0.809707077186
k7 accuracy : 0.753474449433
k8 accuracy : 0.907590335685
k9 accuracy : 0.980885182809
k10 accuracy : 0.899337181954
k11 accuracy : 0.96262561471
k12 accuracy : 0.854479367116
k13 accuracy : 0.865255505666
k14 accuracy : 0.97695103699
k15 accuracy : 0.951464614069


threshold : 0.7
time accurracy : 0.494077400043
weather accuracy : 0.928164777992
k1 accuracy : 0.985246953175
k2 accuracy : 0.916484926235
k3 accuracy : 0.991533033996
k4 accuracy : 0.906264699594
k5 accuracy : 0.975967500535
k6 accuracy : 0.884755184948
k7 accuracy : 0.779345734445
k8 accuracy : 0.942783835792
k9 accuracy : 0.990250160359
k10 accuracy : 0.906179174685
k11 accuracy : 0.966003848621
k12 accuracy : 0.860936497755
k13 accuracy : 0.872354073124
k14 accuracy : 0.982424631174
k15 accuracy : 0.961941415437

threshold : 0.8
time accurracy : 0.494077400043
weather accuracy : 0.945418002993
k1 accuracy : 0.98969424845
k2 accuracy : 0.926918965149
k3 accuracy : 0.996151379089
k4 accuracy : 0.917169125508
k5 accuracy : 0.982381868719
k6 accuracy : 0.966645285439
k7 accuracy : 0.830147530468
k8 accuracy : 0.981526619628
k9 accuracy : 0.993500106906
k10 accuracy : 0.916185589053
k11 accuracy : 0.968740645713
k12 accuracy : 0.87269617276
k13 accuracy : 0.883130211674
k14 accuracy : 0.986572589267
k15 accuracy : 0.969809707077


threshold : 0.9
weather accuracy : 0.954691753973
time accurracy : 0.494077400043
k1 accuracy : 0.992901432542
k2 accuracy : 0.936668804789
k3 accuracy : 0.998075689545
k4 accuracy : 0.92674791533
k5 accuracy : 0.986529826812
k6 accuracy : 0.995082317725
k7 accuracy : 0.856232627753
k8 accuracy : 0.994611930725
k9 accuracy : 0.995082317725
k10 accuracy : 0.925721616421
k11 accuracy : 0.970109044259
k12 accuracy : 0.883472311311
k13 accuracy : 0.893222150951
k14 accuracy : 0.989052811631
k15 accuracy : 0.97686551208
'''






