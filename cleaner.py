#!/usr/bin/env python3

import sys
import json
import shutil
from os import walk, path, remove, chmod, listdir
from re import sub
from pathlib import Path


target_dir = sys.argv[1]

def get_valid_songs(target_dir):
	if not path.isdir(target_dir):
		print(f'Target directory "{target_dir}" was not found.')
		return None

	ok_dirs = set()
	bad_dirs = set()
	dup_dirs = set()

	all_directories = walk(target_dir)
	# We need the immediate children of the target directory and
	# the info.dat file in it. We can get both in one shot by
	# skipping the first return of the walk() generator that lists
	# just the sub directory names and go straight to the next
	# return which includes the sub directory path and its contents.
	next(all_directories)
	for song_dir, _, song_files in all_directories:
		if 'info.dat' in [f.lower() for f in song_files] and song_dir not in ok_dirs:
			ok_dirs.add(song_dir)
		elif song_dir in ok_dirs:
			dup_dirs.add(song_dir)
		else:
			bad_dirs.add(song_dir)
			
	return (ok_dirs, dup_dirs, bad_dirs)	


def parse_song_info(target_dir, info_file='info.dat'):
	with open(f'{target_dir}/{info_file}', 'r') as fp:
		contents = fp.read()
		return json.loads(contents)
	return None


def format_for_xml(subject, lowercase=False):
	regex = r'[^A-Za-z0-9_]'
	if lowercase:
		subject.lower()
	return sub(regex, '_', subject)


# Creates parent directories if they don't exist
def create_dir(target_dir):
	Path(target_dir).mkdir(parents=True, exist_ok=True)
	chmod(target_dir, 0o755)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in listdir(src):
        s = path.join(src, item)
        d = path.join(dst, item)
        if path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def copy_all_files(source_dir, target_dir):
	copytree(source_dir, target_dir)	


def delete_dir(target_dir):
	if path.isdir(target_dir):
		remove(target_dir)


output_dir = 'output'
delete_dir(output_dir)
create_dir(output_dir)

ok_songs, _, _ = get_valid_songs(target_dir)
if len(ok_songs) == 0:
	print(f'No songs in directory "{target_dir}" look valid.')
	sys.exit()

for song_dir in ok_songs:
	song_hash = song_dir.split('/')[1]
	info = parse_song_info(song_dir)
	s_name = format_for_xml(info['_songName'])
	s_auth = format_for_xml(info['_songAuthorName'])
	l_auth = format_for_xml(info['_levelAuthorName'])

	new_song_dirname = f'{s_name}-{s_auth}-{l_auth}-{song_hash}'
	new_song_dir = f'{output_dir}/{new_song_dirname}'
	create_dir(new_song_dir)
	if not path.isdir(new_song_dir):
		print(f'Failed to create directory "{new_song_dir}"! Could not copy files.')
	else:
		copy_all_files(song_dir, new_song_dir)
