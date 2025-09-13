#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r alx_travel_app/requirements.txt
python alx_travel_app/manage.py migrate --noinput
python alx_travel_app/manage.py collectstatic --noinput
