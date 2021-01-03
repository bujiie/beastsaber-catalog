#!/usr/bin/env bash

catalog=$1

echo "Removing 'output', 'unzips', and 'zips' directories before downloading new songs..."
rm -rf "output" "unzips" "zips"
echo "Done."

echo "Downloading song zip files marked in catalog to 'zips' directory..."
./downloader.py "zips" "$catalog"
echo "Done."

echo "Unzipping files in 'zips' to 'unzips'..."
./unzip.py "zips" "unzips"
echo "Done."

echo "Renaming directories in 'unzips' to describe songs..."
./cleaner.py "unzips"
echo "Done."

echo "Removing 'unzips'..."
rm -rf "unzips"
echo "Done."
