#!/usr/bin/env python3

import sys
import time
import html.parser
from re import findall
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from pathlib import Path
from os import chmod, remove, path


def polite_assert(valid, message):
	if not valid:
		print(message)
		sys.exit()


def get_page(url, encoding='utf-8', retries=2):
	try:
		response = urlopen(url)
		return response.read().decode(encoding)
	except HTTPError as e:
		print(f'ERROR: {url}, retries remaining={retries}', e)
		if retries == 0:
			return None
		print(f'Retrying request to {url}')
		return get_page(url, encoding, retries-1)
		


def get_all_matches(subject, search_pattern):
	pass


def get_max_pages(html):
	regex = r'class=\"page-numbers\" href=\".*\">([\d\,]+)</a>'
	results = findall(regex, html)
	if results is None:
		return None
	# findall() will get each pagination link. We assume the last
	# link will be the last available page of songs.
	return int(results[-1].replace(',', ''))


def build_page_url(category, duration, page):
	 return f'https://bsaber.com/songs/{category}/page/{page}/?time={duration}'


def get_song_data(html):
	soup = BeautifulSoup(html, features='html.parser')
	results = soup.find_all('article', {'class': 'post'})

	if len(results) == 0:
		return None
	
	metadatas = []
	for article in results:
		m = {}
		mapper = article.find('div', {'class': 'post-mapper-id-meta'})
		if mapper is not None and mapper.find('a') is not None:
			m['map_author'] = mapper.find('a').getText().strip()
		else:
			m['map_author'] = ''

		publish = article.find('time', {'class': 'published'})
		if publish is not None:
			m['pub_time'] = publish.getText().strip()
		else:
			m['pub_time'] = ''

		song_title_tag = article.find('h4', {'class': 'entry-title'})
		if song_title_tag is not None and song_title_tag.find('a') is not None:
			stl = song_title_tag.find('a')
			m['song_title'] = stl.getText().strip()
			m['song_link'] = stl['href'].strip()
		else:
			m['song_title'] = ''
			m['song_link'] = ''

		m['difficulties'] = list(map(lambda d: d.getText().strip(), article.find_all('a', {'class': 'post-difficulty'})))
		m['categories'] = list(map(lambda c: c.getText().strip(), article.find_all('a', {'class': 'single_category_title'})))
		thumbs_up = article.find('i', {'class': 'fa-thumbs-up'})
		if thumbs_up is not None:
			m['thumbs_up'] = thumbs_up.next_sibling.strip()
		else:
			m['thumbs_up'] = ''

		thumbs_down = article.find('i', {'class': 'fa-thumbs-down'})
		if thumbs_down is not None:
			m['thumbs_down']  = thumbs_down.next_sibling.strip()
		else:
			m['thumbs_down'] = ''

		
		download_link = article.find('a', {'class': '-download-zip'})
		if download_link is not None:
			m['download_link'] = download_link['href'].strip()
		else:
			m['download_link'] = ''
		metadatas.append(m)

	return metadatas
			
class Timer:
	def __init__(self):
		self.times = {}
		self.last_time = None

	def start(self):
		if 'stop' in self.times:
			print('Timer has already been stopped.')
		else:
			self.times['start'] = (self.__now(), 0)

	def split(self, tag):
		last_time = self.last_time
		now = self.__now()	
		self.times[tag] = (now, now - last_time)

	def get(self, tag):
		if tag not in self.times:
			print(f'Could not find tag:{tag} in recorded times.')
			return None
		return self.times[tag]

	def get_all(self):
		return self.times
	
	def stop(self):
		last_time = self.last_time
		now = self.__now()
		self.times['stop'] = (now, now - last_time)

	def __now(self):
		now = time.time_ns()
		self.last_time = now
		return now
		

def quote(string):
	return f'"{string}"'


def create_dir(target_dir):
	Path(target_dir).mkdir(parents=True, exist_ok=True)
	chmod(target_dir, 0o755)


def delete_dir(target_dir):
	if isdir(target_dir):
		remove(target_dir)


polite_assert(len(sys.argv) >= 3, 'Missing arguments.')

target_dir = sys.argv[1]
search_category = sys.argv[2].strip()
search_duration = sys.argv[3].strip()
from_page = int(sys.argv[4].strip())
# inclusive
to_page = int(sys.argv[5].strip())

polite_assert(len(search_category) > 0, 'No search category was found.')
polite_assert(len(search_duration) > 0, 'No search duration was found.')

avail_categories = {'new','top','most-difficult'}
avail_durations = {'24-hours','7-days','30-days','3-months','all'}

polite_assert(search_category in avail_categories, f'Category is not supported. Avail: ({avail_categories})')
polite_assert(search_duration in avail_durations, f'Duration is not supported. Avail: ({avail_durations})')

create_dir(target_dir)


# Initial calls made to the first page of category/duration to parse total number of pages
# that exist.
first_page_url = build_page_url(search_category, search_duration, 1)
first_page_data = get_page(first_page_url)
max_pages = get_max_pages(first_page_data)

if to_page > max_pages:
	to_page = max_pages+1
else:
	# add 1 to make to_page inclusive when used in range()
	to_page += 1

if from_page < 1:
	from_page = 1
elif from_page > max_pages:
	from_page = max_pages

pages_range = range(from_page, to_page)


def thread_task(category, duration, page):
	timer = Timer()
	timer.start()
	page_url = build_page_url(category, duration, page)
	timer.split('page-url')
	page_data = get_page(page_url)
	timer.split('request-page')
	song_data = get_song_data(page_data)
	timer.split('parse-data')
	with open(f'{target_dir}/{category}_{duration}_{page}.txt', 'w') as fp:
		headers = ['select','song/artist','map author','publish date','difficulties','download link','up votes','down votes','song page link']
		fp.write('\t'.join(headers) + '\n')
		for data in song_data:
			line = ['', quote(data['song_title']), quote(data['map_author']), quote(data['pub_time']), quote(','.join(data['difficulties'])), data['download_link'], data['thumbs_up'], data['thumbs_down'], data['song_link']]
			fp.write('\t'.join(line) + '\n')
		fp.close()
	timer.split('write-file')
	return (f'{category}_{duration}_{page}', song_data, timer)


with ThreadPoolExecutor(max_workers=10) as executor:
	futures = []
	for i in pages_range:
		futures.append(executor.submit(thread_task, search_category, search_duration, i))
	
	for future in as_completed(futures):
		identifier, _, _ = future.result()
		print(f'{identifier}...OK')


