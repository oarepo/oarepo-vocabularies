#!/bin/bash

set -e

cd "$(dirname "$0")"

source .venv/bin/activate

python setup.py extract_messages -o oarepo_vocabularies/translations/messages.pot -F babel.cfg

pybabel update -i oarepo_vocabularies/translations/messages.pot -d oarepo_vocabularies/translations/