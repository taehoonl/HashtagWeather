#!/bin/bash
echo
echo "Script for Machine Learning Project, CS 4780"
echo

digits="digits"
train=".train"
model=".model"
# out=".out"
val=".val"
_test=".test"
# traintxt=".train.txt"
# classifytxt="_classify.txt"
echo "Classifying..."
for i in 0.01 0.05 0.1 0.5 1
do
# for i in 0.01 0.1 1
# for w in 1 2 3 4
# for s in 5
	# for d in 1 2
	# do
		# for i in 0.0001 0.0005 0.001 0.005 0.01 0.05 0.1
		# for k in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
		for k in 5
			do
				echo $k $i
				# ./svm_learn -t 0 -c $i ../data/svm/train_data/s$k$train s$k$model$i
				./svm_classify ../data/svm/val_data/s$k$val linear_models/s$k$model$i >> s5_accuracies_c$i.txt
				# ./svm_learn -t 0 -c $i d/s$s$train s5$model$i >> classifystuff.txt
				# ./svm_classify $digits$j$val $digits$j$model $digits$j$out
			done
		# ./svm_classify "digits.test" $digits$j$model $digits$j$out >> "txt/test_classify.txt"
	# done
done

echo "DONE"
echo