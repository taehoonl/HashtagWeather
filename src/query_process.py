from query_tweet import Query
import os
import pdb

directory = '../data/twitDB_12-03-2013'
aggregated_file = '../data/twitDB_12-03-2013/processed_data/tweet_data.txt'

query = Query()
for filename in os.listdir(directory):
	print filename
	if filename.endswith(".txt"):
		query.process_file(directoryc+filename)
		query.save_data(aggregated_file)

query.read_data(aggregated_file)
