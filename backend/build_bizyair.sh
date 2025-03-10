#!/bin/bash

rm -rf dist bizyair.egg-info
python -m build

# test pypi
# twine upload --repository testpypi dist/* --verbose
# pip install -i https://test.pypi.org/simple/ bizyair

# pypi
# twine upload dist/* --verbose
# pip install bizyair
