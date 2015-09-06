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

# TODO: Migrate to generate().
generate_asy() {
	PYTHONPATH=generator venv/bin/python -m generate_asy "$1" /dev/fd/3 3>&1 >&2
}

generate() {
	PYTHONPATH=generator venv/bin/python -m "generate.$1" "$2"
}

for i in src/polyhedra/*.json; do
	name=$(echo "$i" | sed -r 's,^src/polyhedra/(.*)\.json$,\1,')
	
	generate_file "src/$name.asy" generate_asy "$i"
	
	for j in ; do
		generate_file "src/$j/$name.asy" generate "$j" "$i"
	done
	
	for j in model stellation; do
		generate_file "src/$j/$name.scad" generate "$j" "$i"
	done
done
