#!/bin/bash

cp setup-basic.cfg setup.cfg
pip install -e .[tests]
