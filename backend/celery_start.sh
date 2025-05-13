#!/bin/bash

# Ensure we're in the right directory
cd /app/manageRestaurant

# Wait for the backend server to be ready
echo "Waiting for backend server..."
sleep 10

# Start Celery worker
echo "Starting Celery worker..."
celery -A manage_restaurant worker --loglevel=info 