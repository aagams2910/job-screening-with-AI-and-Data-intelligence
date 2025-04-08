import os
from dotenv import load_dotenv

# Try to load the environment variables
load_dotenv()

# Print environment variables loaded
print("Environment variables loaded:")
print(f"GMAIL_USER: {os.getenv('GMAIL_USER')}")
print(f"COMPANY_NAME: {os.getenv('COMPANY_NAME')}")

# Print raw file contents for debugging
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        print("\nRaw .env contents:", f.read())