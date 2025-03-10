#!/bin/bash

rm -rf dist bizyui.egg-info
python -m build

# test pypi
# twine upload --repository testpypi dist/* --verbose

# pypi
# twine upload dist/* --verbose
