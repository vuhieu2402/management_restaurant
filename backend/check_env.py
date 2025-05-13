import os

# Check for environment variables
print("Checking environment variables...")
print(f"OPENROUTER_API_KEY: {'Present' if 'OPENROUTER_API_KEY' in os.environ else 'Missing'}")
if 'OPENROUTER_API_KEY' in os.environ:
    key = os.environ['OPENROUTER_API_KEY']
    print(f"Key starts with: {key[:10]}...")
    print(f"Key length: {len(key)}")

# Other important environment variables
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")
print(f"REDIS_HOST: {os.environ.get('REDIS_HOST', 'Not set')}")
print(f"DEBUG: {os.environ.get('DEBUG', 'Not set')}") 