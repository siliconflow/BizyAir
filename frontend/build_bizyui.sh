#!/bin/bash

rm -rf dist bizyui.egg-info
python -m build

# test pypi
# twine upload --repository testpypi dist/* --verbose
# pip install -i https://test.pypi.org/simple/ bizyui

# pypi
# twine upload dist/* --verbose
# pip bizyui
