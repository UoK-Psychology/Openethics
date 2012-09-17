#!/bin/bash -ex

virtualenv -q ve
source ve/bin/activate
pip install -r requirements.txt
python manage.py jenkins