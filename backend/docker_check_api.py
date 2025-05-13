import os
import requests
import sys

print("=== OpenRouter API Connection Check ===")

# Get the API key from environment variable
api_key = os.environ.get('OPENROUTER_API_KEY')
print(f"API Key from environment: {'Found' if api_key else 'Not found'}")
if api_key:
    print(f"API Key first 4 chars: {api_key[:4]}")
    print(f"API Key last 4 chars: {api_key[-4:]}")
    print(f"API Key length: {len(api_key)}")

api_base = 'https://openrouter.ai/api/v1'
model = 'deepseek/deepseek-chat-v3-0324'

# Test the API connection
headers = {
    'Authorization': f'Bearer {api_key}',
    'HTTP-Referer': 'https://restaurant-management-app.com',
    'X-Title': 'Restaurant Management System',
    'Content-Type': 'application/json'
}

data = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
}

print("\n=== Testing API connection ===")
try:
    print(f"Sending request to {api_base}/chat/completions")
    print(f"Using headers: {headers}")
    
    response = requests.post(
        f"{api_base}/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    if response.status_code == 401:
        print("Authentication error: Check your API key")
        print(f"Response body: {response.text}")
    elif response.status_code == 200:
        print("Connection successful!")
        print(f"Response: {response.text[:200]}...")
    else:
        print(f"Other error: {response.status_code}")
        print(f"Response body: {response.text}")
        
except Exception as e:
    print(f"Exception occurred: {str(e)}")

print("\n=== Environment Variables ===")
for key, value in os.environ.items():
    if 'KEY' in key or 'SECRET' in key:
        print(f"{key}: {'*' * 10}")
    else:
        print(f"{key}: {value}") 