#!/bin/bash

python -m venv venv
. ./venv/bin/activate
export FLASK_APP=ascenda
export FLASK_ENV=development
flask run