#!/bin/bash
git pull || exit 1
source .venv/bin/activate || exit 1
pip3 install -r requirements.txt || exit 1
python3 manage.py runserver &
