import os
import pdb

import numpy as np
import pickle
import svmlight
import svmlight_loader as svml

from parser import Parser
from svm import SVM
from naivebayes import MultiNaiveBayes, NaiveBayes

# global
threshold = 0.5

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
	# print "finished training for w[1-4] naive bayes classifier"

	# classify temporal
	# tweets = validation_data['tweet']
	# for t in tweets:
	# 	# w = time_nb.classify(t)
	# 	# w_sorted = sorted(w, key=lambda (a,b): b)
	# 	# top, dontcare = w_sorted[3]
	# 	top = time_nb.classify_top(t)
	# 	temporal_classifications.append(top)

	# accuracy (binary approach = 0.59)
	# correct = 0
	# total = 0
	# for i in range(len(temporal_classifications)):
	# 	total += 1
	# 	if temporal_classifications[i] == temporal_labels[i]:
	# 		correct += 1
	# print "threshold : {}".format(threshold)
	# print "time accurracy : " + str(float(correct)/float(total))
	pdb.set_trace()

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
	# print "finished training for k[1-15] naive bayes classifier"
	pdb.set_trace()
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
		result = weather_nb.classify_all(t, 0)#threshold)
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

	'''
	write object files for classifiers
	'''
	os.system('rm -r ../data/bayes_model/*')
	pickle_obj("../data/bayes_model/time_nb.obj", time_nb)
	pickle_obj("../data/bayes_model/weather_nb.obj", weather_nb)

	abc = unpickle_obj("../data/bayes_model/weather_nb.obj")
	pdb.set_trace()

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




'''
Multinomial Bayes result

threshold : 0.1
time accurracy : 0.345806591972
k1 accuracy : 0.479930381812
k2 accuracy : 0.483465680409
k3 accuracy : 0.761285760905
k4 accuracy : 0.49271184597
k5 accuracy : 0.49934732949
k6 accuracy : 0.929783530947
k7 accuracy : 0.554008484717
k8 accuracy : 0.863483084956
k9 accuracy : 0.499673664745
k10 accuracy : 0.419721527249
k11 accuracy : 0.412596540846
k12 accuracy : 0.404438159469
k13 accuracy : 0.48607636245
k14 accuracy : 0.595398672903
k15 accuracy : 0.437941912325
weather accuracy : 0.55465752928


threshold : 0.2
time accurracy : 0.345806591972
k1 accuracy : 0.4780811487
k2 accuracy : 0.478896986838
k3 accuracy : 0.765963232895
k4 accuracy : 0.483465680409
k5 accuracy : 0.495485695638
k6 accuracy : 0.93027303383
k7 accuracy : 0.534319590993
k8 accuracy : 0.865441096486
k9 accuracy : 0.488469487654
k10 accuracy : 0.414935276841
k11 accuracy : 0.411835091918
k12 accuracy : 0.401990645056
k13 accuracy : 0.471826389644
k14 accuracy : 0.594854780811
k15 accuracy : 0.43489611661
weather accuracy : 0.550048950288


threshold : 0.3
time accurracy : 0.345806591972
k1 accuracy : 0.477210921353
k2 accuracy : 0.472370281736
k3 accuracy : 0.77227238116
k4 accuracy : 0.473294898292
k5 accuracy : 0.491787229414
k6 accuracy : 0.930762536713
k7 accuracy : 0.518111606657
k8 accuracy : 0.868432502991
k9 accuracy : 0.480909387578
k10 accuracy : 0.410964864571
k11 accuracy : 0.41167192429
k12 accuracy : 0.39976068748
k13 accuracy : 0.455835962145
k14 accuracy : 0.594909170021
k15 accuracy : 0.43157837485
weather accuracy : 0.545991515283

threshold : 0.4
time accurracy : 0.345806591972
k1 accuracy : 0.47606874796
k2 accuracy : 0.470901773088
k3 accuracy : 0.772326770369
k4 accuracy : 0.467420863701
k5 accuracy : 0.48542369194
k6 accuracy : 0.930980093549
k7 accuracy : 0.508865441096
k8 accuracy : 0.869465897966
k9 accuracy : 0.479060154465
k10 accuracy : 0.408734906994
k11 accuracy : 0.411508756663
k12 accuracy : 0.398890460133
k13 accuracy : 0.451430436201
k14 accuracy : 0.594528445556
k15 accuracy : 0.42564995105
weather accuracy : 0.543417092715


threshold : 0.5
time accurracy : 0.345806591972
k1 accuracy : 0.475470466659
k2 accuracy : 0.466931360818
k3 accuracy : 0.773360165343
k4 accuracy : 0.461764385946
k5 accuracy : 0.479767214185
k6 accuracy : 0.931143261177
k7 accuracy : 0.500435113673
k8 accuracy : 0.870009790058
k9 accuracy : 0.479168932884
k10 accuracy : 0.406885673882
k11 accuracy : 0.411563145872
k12 accuracy : 0.398564124878
k13 accuracy : 0.44686174263
k14 accuracy : 0.594474056347
k15 accuracy : 0.419123245948
weather accuracy : 0.541034845353


threshold : 0.6
time accurracy : 0.345806591972
k1 accuracy : 0.474219514848
k2 accuracy : 0.464647014032
k3 accuracy : 0.773686500598
k4 accuracy : 0.458446644186
k5 accuracy : 0.471935168063
k6 accuracy : 0.931360818014
k7 accuracy : 0.493201348852
k8 accuracy : 0.870553682149
k9 accuracy : 0.480528663113
k10 accuracy : 0.405199608398
k11 accuracy : 0.410692918525
k12 accuracy : 0.397530729903
k13 accuracy : 0.444087892962
k14 accuracy : 0.594147721092
k15 accuracy : 0.412433373219
weather accuracy : 0.538844773197


threshold : 0.7
time accurracy : 0.345806591972
k1 accuracy : 0.473022952246
k2 accuracy : 0.461220493854
k3 accuracy : 0.774121614272
k4 accuracy : 0.454530621125
k5 accuracy : 0.466550636354
k6 accuracy : 0.93157837485
k7 accuracy : 0.487544871098
k8 accuracy : 0.870771238986
k9 accuracy : 0.480637441532
k10 accuracy : 0.402860872403
k11 accuracy : 0.410257804852
k12 accuracy : 0.395844664419
k13 accuracy : 0.442293049059
k14 accuracy : 0.59365821821
k15 accuracy : 0.406015446535
weather accuracy : 0.536727219986


threshold : 0.8
time accurracy : 0.345806591972
k1 accuracy : 0.468563037093
k2 accuracy : 0.451647993038
k3 accuracy : 0.773795279017
k4 accuracy : 0.443761557707
k5 accuracy : 0.461166104645
k6 accuracy : 0.931252039595
k7 accuracy : 0.43489611661
k8 accuracy : 0.870608071359
k9 accuracy : 0.478353094746
k10 accuracy : 0.39307081475
k11 accuracy : 0.407592733602
k12 accuracy : 0.384259762863
k13 accuracy : 0.431360818014
k14 accuracy : 0.591537039051
k15 accuracy : 0.398074621995
weather accuracy : 0.527995938939


threshold : 0.9
time accurracy : 0.345806591972
k1 accuracy : 0.465680409007
k2 accuracy : 0.442075492222
k3 accuracy : 0.773468943762
k4 accuracy : 0.433971500054
k5 accuracy : 0.45686935712
k6 accuracy : 0.931197650386
k7 accuracy : 0.408571739367
k8 accuracy : 0.87049929294
k9 accuracy : 0.477102142935
k10 accuracy : 0.38311758947
k11 accuracy : 0.406559338627
k12 accuracy : 0.374904818884
k13 accuracy : 0.421135646688
k14 accuracy : 0.589796584358
k15 accuracy : 0.391384749266
weather accuracy : 0.521755683672

'''

def pickle_obj(filename, obj):
	f = open(filename, "w")
	pickle.dump(obj, f)
	f.close()
	print "finished pickling"

def unpickle_obj(filename):
	f = open(filename, "r")
	obj = pickle.load(f)
	f.close()
	print "finished unpickling"
	return obj


# svm_classify()
bayes_classify()


