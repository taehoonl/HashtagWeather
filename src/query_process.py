from query_tweet import Query
import os
import pdb

aggregated_file = '../data/twitDB/processed/tweet_data.txt'

query = Query()
for filename in os.listdir('../data/twitDB'):
	print filename
	if filename.endswith(".txt"):
		query.process_file('../data/twitDB/'+filename)
		query.save_data(aggregated_file)

query.read_data(aggregated_file)