#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting Django"
python manage.py $1