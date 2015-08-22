#! /usr/bin/env bash

set -e -o pipefail

current_file_name=$1

# This function should be called for each generated file with the file's name as the first argument and the command to call to produce the file's content as the remaining arguments.
function generate_file() {
	file_name=$1
	shift
	generate_command=("$@")
	
	if ! [ "$current_file_name" ]; then
		echo "$file_name"
	elif [ "$current_file_name" == "$file_name" ]; then
		mkdir -p "$(dirname "$file_name")"
		"${generate_command[@]}" > "$file_name"
	fi
}

# Call generate_file for each file to be generated.
# E.g.:
# generate_file src/test.scad echo "cube();"

generate() {
	PYTHONPATH=generator venv/bin/python -m generate_asy "$1" /dev/fd/3 3>&1 >&2
}

for i in src/polyhedra/*.json; do
	generate_file "$(echo "$i" | sed -r 's,^src/polyhedra/(.*)\.json$,src/\1.asy,')" generate "$i"
done
