HashtagWeather
==============

### Project Description

This was a project done by Suchan Lee, Taehoon Lee, Seok Hyun Kim, and Matthew Kim for CS 4780 - Machine Learning taught by Thorsten Joachims in Cornell.

We took part in a Kaggle competition called [Partly Sunny with a Chance of Hashtags](http://www.kaggle.com/c/crowdflower-weather-twitter) and aimed to classify the weather of any selected area by analyzing real-time Tweets from Twitter. The training data that we used were taken from the Kaggle competition.


### Learning Methods

For this project, we attempted to use three learning algorithm: Naive-Bayes, SVM, and Decision Tree. The Naive-Bayes and Decision Tree algorithms were hand-coded and for the SVM classifier we used SVMLight, a lightweight SVM library written by Joachim Thorsten. The wrapper to communicate with SVMLight was custom written.


### Dependencies

This project has the following main dependencies
- SVMLight
- svmlight-loader
- Numpy/Scipy
- ntlk
- tweepy
