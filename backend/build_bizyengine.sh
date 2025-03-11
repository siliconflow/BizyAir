#!/bin/bash

rm -rf dist bizyengine.egg-info
python -m build

# test pypi
# twine upload --repository testpypi dist/* --verbose
# pip install -i https://test.pypi.org/simple/ bizyengine

# pypi
# twine upload dist/* --verbose
# pip install bizyengine
