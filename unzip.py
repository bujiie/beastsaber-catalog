#!/usr/bin/env python3

import sys
import zipfile
from os import walk, path, chmod, remove
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

source_dir = sys.argv[1]
target_dir = sys.argv[2]

def get_all_zipfiles(source_dir):
	if not path.isdir(source_dir):
		print(f'Target directory "{target_dir}" was not found.')
		return None

	contents = walk(source_dir)
	for parent, _, files in contents:
		zipfiles = list(filter(lambda z: z.endswith('.zip'), files))
		zipfiles = list(map(lambda z: (z[:-4], path.abspath(f'./{parent}/{z}')), zipfiles))
		return zipfiles


def unzip(target_dir, zfile_path):
	z_ref = zipfile.ZipFile(zfile_path)
	z_ref.extractall(target_dir)
	z_ref.close()
	return True


def create_dir(target_dir):
	Path(target_dir).mkdir(parents=True, exist_ok=True)
	chmod(target_dir, 0o755)


def delete_dir(target_dir):
	if path.isdir(target_dir):
		remove(target_dir)

def thread_task(target_dir, zfile):
	id, abs_path = zfile
	if unzip(f'{target_dir}/{id}', abs_path):
		return id


create_dir('unzips')
all_zipfiles = get_all_zipfiles(source_dir)

with ThreadPoolExecutor(max_workers=10) as executor:
	futures = []
	for zfile in all_zipfiles:
		futures.append(executor.submit(thread_task, target_dir, zfile))
	
	for future in as_completed(futures):
		id = future.result()
		print(f'Unzipping {id}...OK')


