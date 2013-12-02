from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

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

class listener(StreamListener):
	def on_data(self, data):
		global total

		time = None
		tweet = None
		coordinates = ""
		location = ""
		#try:
		# split up the data
		if '"created_at"' in data:
			time = data.split('"created_at":"')[1].split('","id')[0] # the full time stamp
		# print time			
		if ',"text":"' in data:
			tweet = data.split(',"text":"')[1].split('","source')[0] # the full tweet text
		# print tweet
		if ',"coordinates":' in data:
			coordinates = data.split(',"coordinates":')[1].split(',"place')[0] # the full coordinates
		# print coordinates
		if ',"location:":' in data:
			location = data.split(',"location":"')[1].split(',"url":')[0]

		if time is not None and tweet is not None:
			total += 1
			if total % 1000 == 0:
				print "Saved " + str(total) + " tweets"
			# data is saved in the order of 
			# time, text, location, coordinates
			saveThis = time+"||"+tweet+"||"+location+"||"+coordinates
			saveFile = open('twitDB.txt', 'a')
			saveFile.write(saveThis + "\n")
			saveFile.close()
		return True
		#except BaseException, e:
		#	print "Failed on_data, ", str(e)
			
	
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