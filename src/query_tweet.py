import os
import pdb
import numpy as np
import math
import json
from pygeocoder import Geocoder
import pickle

class Query:

	def __init__(self):
		self.R = 3959
		self.coordinates = 0
		self.locations = 0
		# tweet_data entry = [latitude, longitude, tweet]
		self.entry_length = 3 #
		self.tweet_data = []

	def process_file(self, data_path):
		# process data
		self.tweet_data = []
		with open(data_path) as f:
			content = f.readlines()
			# l = json with 'time' 'text' 'location' 'coordinates'
			for l in content:
				j = json.loads(l)
				self.process_tweet(j)

	def save_data(self, data_path):
		f = open(data_path, 'a')
		print "before"
		pickle.dump(self.tweet_data, f)
		print "after"
		f.close()

	def read_data(self, data_path):
		lists = []
		infile = open(data_path, 'r')
		while 1:
		    try:
		        lists = lists + pickle.load(infile)
		    except (EOFError):
		    	print "done reading in all pickled files"
		        break
		infile.close()
		self.tweet_data = lists

	def count(self):
		return len(self.tweet_data), self.coordinates, self.locations

	def get_lat_lon(self, str):
<<<<<<< HEAD
		try:
			results = [45.0,45.0]
			return results[0], results[1]
			# results = Geocoder.geocode(str)
			# return results.coordinates[0], results.coordinates[1]
		except Exception,e: 
			print e
			return None, None
=======
		return 45.0, 45.0
		# try:
		# 	results = Geocoder.geocode(str)
		# 	print results.coordinates
		# 	return results.coordinates[0], results.coordinates[1]
		# except Exception,e:
		# 	print e
		# 	return None, None
>>>>>>> 7a73b051ff450ea73a8ebfd13067702e445dfe70

	def distance(self, lat1, lon1, lat2, lon2):
		return math.acos( (math.sin(lat1)*math.sin(lat2)) + (math.cos(lat1)*math.cos(lat2)*math.cos(lon1-lon2)) )*self.R

	def process_tweet(self, tweet):

		e = [None] * self.entry_length

		# coordinate
		if not (tweet['coordinates'] == None):
			self.coordinates += 1
			print 'coordinates : ', self.coordinates, tweet['coordinates']['coordinates']
			# coord = map(lambda w: math.radians(float(w)), tweet['coordinates']['coordinates'].split(','))
			e[0] = math.radians(tweet['coordinates']['coordinates'][1]) # latitude (in rad)
			e[1] = math.radians(tweet['coordinates']['coordinates'][0]) # longitude (in rad)
			# e[2] = math.sin(coord[0])
			# e[3] = math.cos(coord[0])
			e[2] = tweet['text']
		# location
		elif not (tweet['location'].strip() == ''):
			self.locations += 1
			print 'locations : ', self.locations, tweet['location'].strip()
			lat, lon = self.get_lat_lon(tweet['location'].strip()) # (in rad)
			if lat is None and lon is None:
				return
			e[0] = math.radians(lat)
			e[1] = math.radians(lon)
			# e[2] = math.sin(lat)
			# e[3] = math.cos(lat)
			e[2] = tweet['text']
		else:
			#print "no coordinate/location data"
			return

		self.tweet_data.append(e)

	def query_coord(self, longitude, latitude, radius):
		matches = []
		lat_rad = math.radians(latitude)
		lon_rad = math.radians(longitude)

		for t in self.tweet_data:
			dist = self.distance(lat_rad, lon_rad, t[0], t[1])
			if dist <= radius:
				matches.append(t[2])
		return matches

	def query_address(self, address, radius):
		lon, lat = self.get_lon_lat(address)
		return self.query_coord(lon, lat, radius)
