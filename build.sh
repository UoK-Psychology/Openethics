#!/bin/bash -ex

virtualenv -q ve
. ve/bin/activate
pip install -r requirements.txt
python manage.py jenkins