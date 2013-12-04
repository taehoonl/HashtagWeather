from query_tweet import Query
import os
import pdb

aggregated_file = '../data/twitDB_12-02-2013/processed_data/tweet_data.txt'

query = Query()
for filename in os.listdir('../data/twitDB_12-02-2013'):
	print filename
	if filename.endswith(".txt"):
		query.process_file('../data/twitDB_12-02-2013/'+filename)
		query.save_data(aggregated_file)

query.read_data(aggregated_file)
pdb.set_trace()