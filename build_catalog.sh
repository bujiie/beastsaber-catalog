#!/usr/bin/env bash

echo "Fetching data from beastsaber.com..."
./catalog.py "data" "$@"
echo "Done."

echo "Merging data into a single TAB separated file..."
./merge_data.py "data"
echo "Done."

