"""
python_arXiv_parsing_example.py

This sample script illustrates a basic arXiv api call
followed by parsing of the results using the 
feedparser python module.

Please see the documentation at 
http://export.arxiv.org/api_help/docs/user-manual.html
for more information, or email the arXiv api 
mailing list at arxiv-api@googlegroups.com.

urllib is included in the standard python library.
feedparser can be downloaded from http://feedparser.org/ .

Author: Julius B. Lucks

This is free software.  Feel free to do what you want
with it, but please play nice with the arXiv API!
"""

from urllib.request import urlopen
import feedparser
import logging
import numpy as np
import pandas as pd
import sys
import time

# Sets up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logpath = '/Users/openamiguel/Desktop/arxiv.log'
handler = logging.FileHandler(logpath)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)

class CArxivParser:
	""" Parses one category from Arxiv """
	def __init__(self, category, outpath):
		# Base api query url
		self.base_url = 'http://export.arxiv.org/api/query?'
		self.category = category

	def get_feed(self, start, max_results):
		""" Returns a feed object built from reading Arxiv data """
		# Search parameters: category, start, and end
		search_query = 'all:{}'.format(self.category)
		
		query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
															 start,
															 max_results)
		
		# Opensearch metadata such as totalResults, startIndex, 
		# and itemsPerPage live in the opensearch namespase.
		# Some entry metadata lives in the arXiv namespace.
		# This is a hack to expose both of these namespaces in
		# feedparser v4.1
		feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
		feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
		
		# perform a GET request using the self.base_url and query
		response = urlopen(self.base_url + query).read()
		
		# parse the response using feedparser
		feed = feedparser.parse(response)
		
		# print out feed information
		logger.info('Feed title: {}'.format(feed.feed.title))
		logger.info('Unique identifier: {}'.format(feed.feed.id))
		logger.info('Feed last updated: {}'.format(feed.feed.updated))
		
		# print opensearch metadata
		logger.info('Total results for this query: {}'.format(feed.feed.opensearch_totalresults))
		logger.info('Items per page for this query: {}'.format(feed.feed.opensearch_itemsperpage))
		logger.info('Start index for this query: {}'.format(feed.feed.opensearch_startindex))
		
		return feed
	
	def get_total_results(self):
		initial_feed = self.get_feed(self.category, start=0, max_results=1)
		total_results = int(initial_feed.feed.opensearch_totalresults)
		return total_results
	
	def parse_feed(self, feed, header=False):
		""" Parses the feed object returned by get_feed"""
		# Save data to dataframe
		parse_df = pd.DataFrame()
		# Run through each entry, and print out information
		for entry in feed.entries:
			# Save new row as (mostly) blank dictionary
			new_row = {'data_source': feed.feed.id, 'last_updated': feed.feed.updated, 
			  'arxiv_id':'', 'publication_timestamp':'', 'publication_year':'', 
			  'title':'', 'authors':'N/A', 'absolute_url':'N/A', 'pdf_url':'N/A', 
			  'journal_ref':'N/A', 'category':'', 'abstract':'N/A', 'comments':'N/A'}
			# Save the arxiv id to new row
			arxiv_id = entry.id.split('/abs/')[-1]
			logger.info('arxiv-id: {}'.format(arxiv_id))
			new_row['arxiv_id'] = arxiv_id
			# Save the publication timestamp and year to new row
			timestamp = entry.published
			year = timestamp.split('-')[0]
			logger.debug('Published: {}'.format(timestamp))
			new_row['publication_timestamp'] = timestamp
			logger.debug('Year Published: {}'.format(year))
			new_row['publication_year'] = year
			# Save the title to new row
			title = entry.title
			title = title.replace('\t', ' ')
			title = title.replace('\n', ' ')
			title = title.replace('  ', ' ')
			logger.info('Title:  {}'.format(title))
			new_row['title'] = title
			# Saves all authors to new row
			try:
				authors_all = '|'.join(author.name for author in entry.authors)
				logger.debug('Authors: {}'.format(authors_all))
				new_row['authors'] = authors_all
			except AttributeError:
				pass
			# Save the abs and pdf links to new row
			for link in entry.links:
				if link.rel == 'alternate':
					logger.info('Absolute page link: {}'.format(link.href))
					new_row['absolute_url'] = link.href
				elif link.title == 'pdf':
					logger.info('PDF link: {}'.format(link.href))
					new_row['pdf_url'] = link.href
			# Saves the journal reference (if any) to new row
			try:
				journal_ref = entry.arxiv_journal_ref
				journal_ref = journal_ref.replace('\t', ' ')
				journal_ref = journal_ref.replace('\n', ' ')
				journal_ref = journal_ref.replace('  ', ' ')
				logger.debug('Journal reference: {}'.format(journal_ref))
				new_row['journal_ref'] = journal_ref
			except AttributeError:
				pass
			# Saves the comment to new row
			try:
				comment = entry.arxiv_comment
				comment = comment.replace('\t', ' ')
				comment = comment.replace('\n', ' ')
				comment = comment.replace('  ', ' ')
				logger.debug('Comments: {}'.format(comment))
				new_row['comments'] = comment
			except AttributeError:
				pass
			# Since the <arxiv:primary_category> element has no data, only
			# attributes, feedparser does not store anything inside
			# entry.arxiv_primary_category
			# This is a dirty hack to get the primary_category, just take the
			# first element in entry.tags.  If anyone knows a better way to do
			# this, please email the list!
			cat = entry.tags[0]['term']
			logger.info('Primary Category: {}'.format(cat))
			new_row['category'] = cat
			# Get all the categories
			all_categories = [t['term'] for t in entry.tags]
			logger.debug('All Categories: {}'.format((', ').join(all_categories)))
			# The abstract is in the <summary> element (re-formatted to remove newlines)
			abstract = entry.summary
			abstract = abstract.replace('\t', ' ')
			abstract = abstract.replace('\n', ' ')
			abstract = abstract.replace('  ', ' ')
			logger.debug('Abstract: {}'.format(abstract))
			new_row['abstract'] = abstract
			# Save new row to dataframe
			parse_df = parse_df.append(new_row, ignore_index=True)
		outfile = open(self.outpath, 'a+')
		parse_df.to_csv(outfile, sep='\t', index=False, header=header)
		outfile.close()

class CArxivParserMulti:
	""" Parses multiple categories from Arxiv """
	def __init__(self, categories, delay=5, max_results=100):
		self.categories = categories
		self.delay = delay
		self.max_results = max_results
	
	def parse_all(self):
		for cat in self.categories:
			# Gets the parser object and number of total results
			parser = CArxivParser(cat, outpath)
			total_results = parser.get_total_results()
			# Gets a list of start indexes for each search page
			starts = list(np.arange(0, total_results, self.max_results))
			starts.append(total_results)
			# Iterates through each start and end index
			for start, idx in zip(starts[:-1], np.arange(0, len(starts) - 1)):
				increment = starts[idx + 1] - start
				if idx != len(starts) - 1:
					increment -= 1
				# Gets the feed and parses it, downloading data in the process
				feed = parser.get_feed(cat, start=start, max_results=increment)
				parser.parse_feed(feed, header=header)
				# Implements time delay to ease load on the API
				logger.info("Snoozing for {0:d} seconds".format(self.delay))
				time.sleep(self.delay)
		return

if __name__ == "__main__":
	""" Iterates through a list of quant-fin categories and prints output """
	prompts = sys.argv
	outpath = prompts[prompts.index("-filepath") + 1]
	# Sets the header argument
	header = True
	# Runs the code
	sub_categories = ['CP', 'EC', 'GN', 'MF', 'PN', 'PR', 'RM', 'ST', 'TR']
	true_categories = ['q-fin.{}'.format(x) for x in sub_categories]
	parser = CArxivParserMulti(true_categories)
	parser.parse_all()
