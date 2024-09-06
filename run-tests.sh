#!/bin/bash

set -e

OAREPO_VERSION="${OAREPO_VERSION:-12}"


VENV=".venv"

if test -d $VENV ; then
  rm -rf $VENV
fi

python3 -m venv $VENV
. $VENV/bin/activate
pip install -U setuptools pip wheel

echo "Installing oarepo version $OAREPO_VERSION"
pip install "oarepo==${OAREPO_VERSION}.*"
pip install -e ".[tests]"

curl -L -o forked_install.sh https://github.com/oarepo/nrp-devtools/raw/main/tests/forked_install.sh
sh forked_install.sh invenio-records-resources


pip uninstall -y uritemplate
pip install uritemplate

invenio index destroy --force --yes-i-know || true

pytest -k "not test_cache and not test_complex_import" tests
pytest -k "test_complex_import" tests
pytest -k "test_cache" tests
