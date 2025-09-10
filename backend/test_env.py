#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variables Test ===")
print(f"DATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not Set'}")
print(f"NEON_DB_URL: {'Set' if os.getenv('NEON_DB_URL') else 'Not Set'}")
print(f"JWT_SECRET_KEY: {'Set' if os.getenv('JWT_SECRET_KEY') else 'Not Set'}")
print(f"GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not Set'}")

# Check if .env file exists
env_file_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file_path):
    print(f"✅ .env file found at: {env_file_path}")
    with open(env_file_path, 'r') as f:
        lines = f.readlines()
        print(f"📄 .env file contains {len(lines)} lines")
else:
    print(f"❌ .env file not found at: {env_file_path}")

print("================================") 