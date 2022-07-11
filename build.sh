#!/bin/bash

set -e

cp oarepo-vocabularies/oarepo_vocabularies/version.py oarepo-vocabularies-basic/oarepo_vocabularies_basic/
cp oarepo-vocabularies/oarepo_vocabularies/version.py oarepo-vocabularies-model-builder/oarepo_vocabularies_model_builder/

cp -r oarepo-vocabularies/oarepo_vocabularies/models/*yaml oarepo-vocabularies-model-builder/oarepo_vocabularies_model_builder/models/

mkdir dist

# create library distribution
(
  cd oarepo-vocabularies
  cat setup.cfg
  python setup.py sdist bdist_wheel
  cp dist/* ../dist/
)

# create basic data model entry points and package
(
  cd oarepo-vocabularies-basic
  cat setup.cfg
  python setup.py sdist bdist_wheel
  cp dist/* ../dist/
)

# create model builder extension package
(
  cd oarepo-vocabularies-model-builder
  cat setup.cfg
  python setup.py sdist bdist_wheel
  cp dist/* ../dist/
)

# just list created stuff
ls -la dist

for i in dist/*.tar.gz; do
  echo
  echo Listing $i
  tar -tf $i
done

