#!/bin/bash

# Simple script to check if our Django server is running properly

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Try to connect to server
curl -f http://localhost:8000/api/ || echo "Server is not responding. Check logs for errors."

# If we got here without error, server is running
echo "Server check completed." 