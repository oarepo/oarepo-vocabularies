#!/bin/bash

cd $(dirname $0)

./generate_setup_cfg.sh

cp setup-basic-local.cfg setup.cfg
source .venv/bin/activate

pip install -e .[tests,elasticsearch7,postgresql]
