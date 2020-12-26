#!/bin/bash

python -m venv venv
. ./venv/bin/activate
export FLASK_APP=ascenda
flask run --host=0.0.0.0