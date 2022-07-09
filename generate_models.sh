#! /bin/bash

cd $(dirname "$0")

test -f .venv-model-builder/bin/oarepo-compile-model || (
  echo "model-builder not installed, installing it to .venv-model-builder virtualenv"
  python3.10 -m venv .venv-model-builder
  source .venv-model-builder/bin/activate
  pip install -U setuptools pip wheel
  pip install oarepo-model-builder
)

# clean previous sources, except of models and common packages
rm -rf oarepo_vocabularies/basic

.venv-model-builder/bin/oarepo-compile-model -vvv --output-directory . oarepo_vocabularies/models/hvocabulary-basic.yaml