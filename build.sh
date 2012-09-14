#!/bin/bash -ex
cd $WORKSPACE
virtualenv -q ve
source ./ve/bin/activate
pip install -E ./ve -r requirements.txt
cd $WORKSPACE/projectname
python manage.py migrate
python manage.py jenkins