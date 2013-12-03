import pdb
from collections import Counter

from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse
# from django.views.generic import FormView

from website.forms import TweetForm
from src.query_tweet import Query
from website.classifiers import Classifiers


class Views:

	def __init__(self):
		self.classifier = Classifiers()
		self.classifier.initialize()

	def home(self, request):

		form = TweetForm()
		context = {}

		if request.method == 'GET':
			try:
				form = TweetForm(request.GET)
				if form.is_valid():
					form_data = form.cleaned_data
					location = form_data['location']
					classifier = form_data['classifier']
					lat, lng = form.get_lat_lng(location)
					forecast = self.forecast(lat, lng, form)

					tweets = self.get_relevant_tweets(lat, lng)
					code, label1, label2 = self.classify_many_tweets(classifier, tweets)
					context['location'] = forecast['location']['city']
					context['actual_condition'] = forecast['condition']['text']
					context['temp'] = forecast['condition']['temp']
					context['tweet_conditions'] = [label1, label2]
					context['tweet_code'] = 'G'

				else:
					form = TweetForm()
			except:
				form = TweetForm()

		context['form'] = form

		return render_to_response('home.html',
			context_instance = RequestContext(request, context))

	def forecast(self, lat, lng, form):
		zipcode = form.get_zipcode(lat, lng)
		forecast = form.get_true_forecast(zipcode)
		return forecast

	def get_relevant_tweets(self, lat, lng, rad=15):
		tweets = self.classifier.tweet_querier.query_coord(lng, lat, rad)
		return tweets

	def classify_many_tweets(self, classifier, tweets):
		condition_map = {}
		condition_list = []
		code_list = []
		print 'Classifying tweets with {}........'.format(classifier)
		for tweet in tweets:
			code, conditions = self.classify(classifier, tweet)
			for condition in conditions:
				if condition != "I can't tell":
					try:
						condition_map[condition] += 1
					except:
						condition_map[condition] = 1

		keys = condition_map.keys()
		for key in keys:
			condition_list.append([condition_map[key], key])
		condition_list.sort(reverse=True)

		code = None
		print condition_list
		return code, condition_list[0][1], condition_list[1][1]

	def classify(self, classifier, tweet):
		if classifier == 'svm':
			code, conditions = self.classifier.classify_with_svm(tweet)
		if classifier == 'bayes':
			code, conditions = self.classifier.classify_with_bayes(tweet)
		if classifier == 'dt':
			code, conditions = self.classifier.classify_with_dt(tweet)
		return code, conditions



