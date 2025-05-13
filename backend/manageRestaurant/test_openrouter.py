import os
import requests
from django.conf import settings
import sys
import django

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage_restaurant.settings')
django.setup()

from django.conf import settings

# Get the API key from settings
api_key = settings.OPENROUTER_API_KEY

print(f"API Key from settings: {api_key}")
print(f"API Base URL: {settings.OPENROUTER_API_BASE}")
print(f"Model: {settings.OPENROUTER_MODEL}")

# Test a simple request to OpenRouter
headers = {
    'Authorization': f'Bearer {api_key}',
    'HTTP-Referer': 'https://restaurant-management-app.com',
    'X-Title': 'Restaurant Management System',
    'Content-Type': 'application/json'
}

data = {
    "model": settings.OPENROUTER_MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
}

try:
    response = requests.post(
        f"{settings.OPENROUTER_API_BASE}/chat/completions",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("Authentication error: Check your API key")
    elif response.status_code == 200:
        print("Connection successful!")
    else:
        print(f"Other error: {response.status_code}")
        
except Exception as e:
    print(f"Exception occurred: {str(e)}") 