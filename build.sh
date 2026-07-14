#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

# Run migrations and static collection
python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Seed the database with sample data so the live deployment has content
python seed_data.py
