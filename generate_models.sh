#! /bin/bash

cd $(dirname "$0")

test -f .venv-model-builder/bin/oarepo-compile-model || (
  echo "model-builder not installed, installing it to .venv-model-builder virtualenv"
  python3.10 -m venv .venv-model-builder
  source .venv-model-builder/bin/activate
  pip install -U setuptools pip wheel
  pip install oarepo-model-builder
  pip install -e oarepo-oarepo-vocabularies-model-builder
)

# clean previous sources, except of models and common packages
rm -rf oarepo-vocabularies-basic/oarepo_vocabularies_basic

.venv-model-builder/bin/oarepo-compile-model -vvv --output-directory oarepo-vocabularies-basic \
  oarepo-vocabularies/oarepo_vocabularies/models/hvocabulary-basic.yaml

cp oarepo-vocabularies/oarepo_vocabularies/version.py oarepo-vocabularies-basic/oarepo_vocabularies_basic/


# generate test model
test -d tests/mock_module_gen && rm -rf tests/mock_module_gen
.venv-model-builder/bin/oarepo-compile-model --output-directory tests -vvv tests/test_model.yaml