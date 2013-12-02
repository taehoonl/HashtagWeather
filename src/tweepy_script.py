from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from pprint import pprint

"""Code to stream the tweets live from the web.
The following library was used - tweepy - accessible from 
https://github.com/tweepy/tweepy.git

=======Install directions for tweepy=======
python setup.py install
===========================================

Data is stored in the format of a String, where we store only 
those tweets that contain words related to the weather.
"""

consumer_key = 'GsnpNuqVcreEaSdBgyGGw'
consumer_secret = 'DrCjrauLjvbfpXe7qSb5N8GQ6bp7yPTmpEVWZzqDjQ'
access_token = '1878195553-HTpislJVIvUrvH9RdferyT92bmYcLwlvEbrhpIc'
access_secret = 'uYzyPFFHwrjjFKCiuLDn2nlaaQQcMnQfb3e6ajmHZUluk'

total = 0
file_count = 1
class listener(StreamListener):
	def on_data(self, data):
		global total
		global file_count
		try:
			tweet = json.loads(data)
			#pprint (tweet)
			time = tweet["created_at"]
			text = tweet["text"]
			coordinates = tweet["coordinates"]
			location = tweet["user"]["location"]
			
			if total % 1000 == 0:
				print "Saved " + str(total) + " tweets"
				file_count += 1
			# make json in the order of time, text, location, coordinates
			if location is not "" or 'null' not in coordinates:
				total += 1
				l = {'time': time, 'text': text, 'location': location, 'coordinates': coordinates}
				saveThis = json.dumps(l)
				saveFile = open('../data/twitDB_' + file_count + '.txt', 'a')
				saveFile.write(saveThis + "\n")
				saveFile.close()
			return True
		except BaseException, e:
			print "Failed on_data, ", str(e)
			pprint(tweet)
			
	
	def on_error(self, status):
		print status
		

# code to run the twitterstream
authenticate = OAuthHandler(consumer_key, consumer_secret)
authenticate.set_access_token(access_token, access_secret)
print "Started streaming..."
twitterStream = Stream(authenticate, listener())
#twitterStream.filter(locations = [-122.75,36.8,-121.75,37.8])

# filter is based on the top used words at weather.com
twitterStream.filter(track = ["undercast, thunderstorm, overcast, sunshine, rainbow, sky, snowfall, snowflakes, hurricane, humidity, breeze, muggy, mist, misty, downpour, drizzle, drizzling, pouring, gust, frost, frosty, hail, heat, sunny, sun, cloud, cloudy, cold, rain, rainy, damp, humid, snow, snowy, snowing, raining, tornado, wind, windy, storm, stormy, thunder, icy, scorching, burning, monsoon, lightning, temperature, steaming, shitty, weather, foggy, fog, winter, summer, spring, autumn, blizzard, freezing, dusty, melting, clear, climate, forecast, precipitation, degrees, celsius, fahrenheit, cyclone, typhoon, "])


# code to get the past tweets
#t = Twitter(auth = OAuth(access_token, access_secret, consumer_key, consumer_secret))
#list_of_words = ["car", "crash"]
#data = t.search.tweets(q = list_of_words, count = 1000000000000000, until='2013-12-01')
#print str(data)
#file = open('test.txt', 'a')
#file.write(str(data))
#file.close()