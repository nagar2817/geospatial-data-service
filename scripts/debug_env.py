#!/usr/bin/env python3
"""Debug environment loading"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=== Environment Debug ===")

# Check .env file existence
env_path = Path(".env")
print(f"Current directory: {Path.cwd()}")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    print(f".env file location: {env_path.absolute()}")
    with open(env_path) as f:
        content = f.read()
        print(f".env file content:\n{content}")
else:
    print("❌ .env file not found!")

# Load environment
load_dotenv()

# Check what's actually loaded
print("\n=== Environment Variables ===")
db_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
for var in db_vars:
    value = os.getenv(var)
    print(f"{var}: {value if var != 'DB_PASSWORD' else '***' if value else 'NOT SET'}")

# Check all environment variables starting with DB_
print("\n=== All DB_ Environment Variables ===")
for key, value in os.environ.items():
    if key.startswith("DB_"):
        display_value = value if key != "DB_PASSWORD" else "***" if value else "NOT SET"
        print(f"{key}: {display_value}")