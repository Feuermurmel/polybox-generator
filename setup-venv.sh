#! /usr/bin/env bash

set -e -o pipefail

cd "$(dirname "$BASH_SOURCE")"

find_command() {
	for i in "$@"; do
		if which "$i" > /dev/null; then
			echo "$i"
			return
		fi
	done
	
	echo "None of these commands found: $@" >&2
	false
}

setup_venv() {
	VENV_PATH=$1
	PYTHON_COMMAND=$2
	VIRTUALENV_COMMAND=$(find_command virtualenv{-3{.{5,4},},})
	
	rm -rf "$VENV_PATH"
	"$VIRTUALENV_COMMAND" -p "$PYTHON_COMMAND" --system-site-packages "$VENV_PATH"
	. "$VENV_PATH/bin/activate"
}

(
	PYTHON_COMMAND=$(find_command python3{.{5,4},})
	
	setup_venv venv "$PYTHON_COMMAND"
	pip install cython
	pip install 'https://github.com/Feuermurmel/pyclipper/archive/master.zip'
	pip install numpy
)
