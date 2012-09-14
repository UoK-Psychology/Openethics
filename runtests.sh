#!/bin/bash
python manage.py test root ethicsapplication checklist basicapplication --verbosity=2 --with-coverage --cover-package=root,ethicsapplication,checklist,basicapplication