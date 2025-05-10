#!/bin/bash
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Database setup
python manage.py migrate --no-input  # --no-input prevents hangs

# Static files
python manage.py collectstatic --no-input

# Verify port is available
echo "--- PORT $PORT is available ---"