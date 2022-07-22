#!/bin/bash

set -e

cp oarepo-vocabularies/oarepo_vocabularies/version.py oarepo-vocabularies-basic/oarepo_vocabularies_basic/
cp oarepo-vocabularies/oarepo_vocabularies/version.py oarepo-vocabularies-model-builder/oarepo_vocabularies_model_builder/

cp -r oarepo-vocabularies/oarepo_vocabularies/models/*yaml oarepo-vocabularies-model-builder/oarepo_vocabularies_model_builder/models/

test -d dist && rm -rf dist

mkdir dist

# create library distribution
(
  cd oarepo-vocabularies
  test -d dist && rm -rf dist
  cp ../README.rst .
  cat setup.cfg
  python setup.py sdist bdist_wheel
  cp dist/*.tar.gz  ../dist/
  cp dist/*.whl  ../dist/
)

# create basic data model entry points and package
(
  cd oarepo-vocabularies-basic
  test -d dist && rm -rf dist
  cp ../README.rst .
  cat setup.cfg
  python setup.py sdist bdist_wheel
  cp dist/*.tar.gz  ../dist/
  cp dist/*.whl  ../dist/
)

# create model builder extension package
(
  cd oarepo-vocabularies-model-builder
  test -d dist && rm -rf dist
  cp ../README.rst .
  cat setup.cfg
  python setup.py sdist bdist_wheel
  cp dist/*.tar.gz  ../dist/
  cp dist/*.whl  ../dist/
)

# just list created stuff
ls -la dist

for i in dist/*.tar.gz; do
  echo
  echo Listing $i
  tar -tf $i
done

