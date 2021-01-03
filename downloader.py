#!/usr/bin/env python3

import sys
from os import path, chmod
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

target_dir = sys.argv[1]
csv_file = sys.argv[2]


def read_selected_songs(csv_file):
	selected = []
	if not path.isfile(csv_file):
		print(f'File "{csv_file}" cannot be found.')
		return None
	with open(csv_file) as fp:
		for i,entry in enumerate(fp):
			if i == 0:
				continue
			if entry.startswith('x\t'):
				selected.append(entry.strip())
		fp.close()
	return selected


def download_zip(target_dir, url):
	zipname = url.split('/')[-1]
	try: 
		# fake browser headers
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
		with urlopen(Request(url=url, headers=headers)) as zipfile:
			with open(f'{target_dir}/{zipname}', 'wb') as fp:
				fp.write(zipfile.read())
				fp.close()
	except HTTPError as e:
		print(f'ERROR: {url}', e)
		return False
	return True


def create_dir(target_dir):
	Path(target_dir).mkdir(parents=True, exist_ok=True)
	chmod(target_dir, 0o755)


create_dir(target_dir)
selected_songs = read_selected_songs(csv_file)

def thread_task(target_dir, song):
	meta = song.split('\t')
	if download_zip(target_dir, meta[5]):
		return (meta[1], meta[2], meta[5].split('/')[-1])


with ThreadPoolExecutor(max_workers=10) as executor:
	futures = []
	for song in selected_songs:
		futures.append(executor.submit(thread_task, target_dir, song))

	for future in as_completed(futures):
		song_title, map_author, id = future.result()
		print(f'{song_title} / {map_author} / {id}...OK')
