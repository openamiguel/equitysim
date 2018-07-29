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

# Base api query url
BASE_URL = 'http://export.arxiv.org/api/query?'
# File path for logger
LOGGER_PATH = '/Users/openamiguel/Desktop/arxiv.log'
# Time delay for mercy on the API
TIME_DELAY = 5
# Max results for each API query
MAX_RESULTS = 100

def get_feed(category, start, max_results=MAX_RESULTS):
	""" Returns a feed object built from reading Arxiv data """
	# Search parameters: category, start, and end
	search_query = 'all:{}'.format(category)
	
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
	
	# perform a GET request using the BASE_URL and query
	response = urlopen(BASE_URL + query).read()
	
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

def parse_feed(outpath, feed, header=False):
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
		"""
		# feedparser v4.1 only grabs the first author
		author_string = entry.author
		"""
		
		"""
		grab the affiliation in <arxiv:affiliation> if present
		- this will only grab the first affiliation encountered
		  (the first affiliation for the first author)
		Please email the list with a way to get all of this information!
		"""
		
		"""
		try:
			author_string += ' ({})'.format(entry.arxiv_affiliation)
		except AttributeError:
			pass
		
		print('Last Author:  {}'.format(author_string))
		"""
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
	outfile = open(outpath, 'a+')
	parse_df.to_csv(outfile, sep='\t', index=False, header=header)
	outfile.close()

if __name__ == "__main__":
	prompts = sys.argv
	outpath = prompts[prompts.index("-filepath") + 1]
	""" Iterates through a list of quant-fin categories and prints output """
	# Sets up the logger
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	
	# Tries to get user input on the logpath
	try: 
		logpath = prompts[prompts.index("-logpath") + 1]
	except ValueError:
		logpath = LOGGER_PATH
	handler = logging.FileHandler(logpath)
	handler.setLevel(logging.DEBUG)
	
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	
	logger.addHandler(handler)
	
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(formatter)
	consoleHandler.setLevel(logging.INFO)
	
	logger.addHandler(consoleHandler)
	# Sets the header argument
	header = True
	# Runs the code
	sub_categories = ['CP', 'EC', 'GN', 'MF', 'PN', 'PR', 'RM', 'ST', 'TR']
	true_categories = ['q-fin.{}'.format(x) for x in sub_categories]
	for cat in true_categories:
		initial_feed = get_feed(cat, start=0, max_results=1)
		total_results = int(initial_feed.feed.opensearch_totalresults)
		starts = list(np.arange(0, total_results, MAX_RESULTS))
		starts.append(total_results)
		for start, idx in zip(starts[:-1], np.arange(0, len(starts) - 1)):
			increment = starts[idx + 1] - start
			if idx != len(starts) - 1:
				increment -= 1
			feed = get_feed(cat, start=start, max_results=increment)
			parse_feed(outpath, feed, header=header)
			logger.info("Snoozing for {0:d} seconds".format(TIME_DELAY))
			time.sleep(TIME_DELAY)
