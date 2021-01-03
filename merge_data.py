#!/usr/bin/env python3

import sys
from os import walk, path

target_dir = sys.argv[1]

def get_csvs(target_dir):
	if not path.isdir(target_dir):
		print(f'Target directory "{target_dir}" was not found.')
		return None

	csv_files = set()
	gen = walk(target_dir)
	parent, _, files = next(gen)
	files = list(filter(lambda f: 'merge' not in f, files))
	return (parent, files)

def read_data(filepath):
	with open(filepath) as fp:
		data = fp.readlines()
		fp.close()
		return data

def write_data(write_to, data=[], inc_headers=False):
	if len(data) == 0:
		print('No data to write.')
		return None

	with open(write_to, 'a+') as fp:
		if not inc_headers:
			data = data[1:]	
			
		for d in data:
			fp.write(d)
		fp.close()

target_filepath = None
parent, csvs = get_csvs(target_dir)
inc_headers = True
for csv in csvs:
	if target_filepath is None:
		prefix = csv.rsplit('_', 1)[0]
		target_filepath = f'{parent}/{prefix}_merge.txt'
	filepath = f'{parent}/{csv}'
	print(f'Reading {filepath}...')
	data = read_data(filepath)
	print(f'Writing {filepath} data to {target_filepath}...')
	write_data(target_filepath, data, inc_headers)
	inc_headers = False




