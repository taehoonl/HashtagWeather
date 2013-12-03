#!/bin/bash
echo
echo "Script for Machine Learning Project, CS 4780"
echo

digits="digits"
train=".train"
model=".model"
# out=".out"
# val=".val"
# traintxt=".train.txt"
# classifytxt="_classify.txt"

#for w in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
# for w in 1 2 3 4
for s in 5
	do
	echo "Training classifiers..."
	# for i in 0.0001 0.0005 0.001 0.005 0.01 0.05 0.1
	for i in 0.01 0.1 1
		do
			./svm_learn -t 0 -c $i ../data/svm/train_data/s$s$train s5$model$i
			# ./svm_classify $digits$j$val $digits$j$model $digits$j$out
		done
	# ./svm_classify "digits.test" $digits$j$model $digits$j$out >> "txt/test_classify.txt"
done

echo "DONE"
echo