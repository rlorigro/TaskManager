#!/usr/bin/env bash
set -e
# This is a script which updates the pip and conda builds so that pip install and conda install work with new master
rm -r dist
python3 setup.py sdist bdist_wheel
twine upload dist/*

