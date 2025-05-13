#!/bin/bash

# Check OpenRouter API connection
echo "Checking OpenRouter API connection..."
python docker_check_api.py

# Apply database migrations
echo "Applying database migrations..."
python manageRestaurant/manage.py migrate --noinput

# Initialize sample data
echo "Loading initial data..."
python manageRestaurant/docker_seed_data.py

# Initialize MinIO
echo "Initializing MinIO storage..."
python manageRestaurant/init_minio.py

# Start server with Daphne for WebSocket support
echo "Starting Django server with Daphne..."
cd manageRestaurant && daphne -b 0.0.0.0 -p 8000 manage_restaurant.asgi:application 