# import pdb, urllib2, json
from pygeocoder import Geocoder
import pywapi

from django import forms

class TweetForm(forms.Form):
	CLASSIFIER_CHOICES = (
		('svm', 'SVM'),
		('dt', 'Decision Tree'),
		('bayes', 'Naive Bayes Classifier'),
	)
	location = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'placeholder':'LOCATION: City, State or Zipcode'}))
	classifier = forms.ChoiceField(choices=CLASSIFIER_CHOICES)

	def get_lat_lng(self, address_str):
		results = Geocoder.geocode(address_str)
		return results.coordinates[0], results.coordinates[1]

	def get_zipcode(self, lat, lng):
		results = Geocoder.reverse_geocode(lat, lng)
		return results[0].postal_code

	def get_true_forecast(self, zipcode):
		yahoo_result = pywapi.get_weather_from_yahoo(zipcode)
		return yahoo_result