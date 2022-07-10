#!/bin/bash

set -e

rm -rf *.egg-info || true
./generate_setup_cfg.sh

# create library distribution
cp setup-library.cfg setup.cfg
python setup.py sdist bdist_wheel
rm -rf *.egg-info || true

# create basic data model entry points and package
cp setup-basic.cfg setup.cfg
python setup.py sdist bdist_wheel
rm -rf *.egg-info || true

# create model builder extension package
cp -r oarepo_vocabularies/models oarepo_vocabularies_model_builder/
cp setup-model-builder.cfg setup.cfg
python setup.py sdist bdist_wheel
rm -rf *.egg-info || true

# just list created stuff
ls -la dist

for i in dist/*.tar.gz ; do
  echo
  echo Listing $i
  tar -tf $i
done