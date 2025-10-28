#!/usr/bin/env python3
"""
Test self-hosted Bot API functionality
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_self_hosted_api():
    """Test if self-hosted Bot API works"""
    print("🔍 Testing self-hosted Bot API...")
    
    # Check environment variables
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    print(f"📋 Environment check:")
    print(f"   TELEGRAM_API_ID: {'✅' if api_id else '❌'}")
    print(f"   TELEGRAM_API_HASH: {'✅' if api_hash else '❌'}")
    
    if not api_id or not api_hash:
        print("❌ Missing TELEGRAM_API_ID or TELEGRAM_API_HASH")
        print("   Get them from: https://my.telegram.org/apps")
        return False
    
    # Check if telegram-bot-api binary exists
    import shutil
    telegram_bot_api_path = shutil.which("telegram-bot-api")
    
    if not telegram_bot_api_path:
        # Try common locations
        possible_paths = [
            "/usr/local/bin/telegram-bot-api",
            "/usr/bin/telegram-bot-api",
            "./telegram-bot-api"
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                telegram_bot_api_path = path
                break
    
    print(f"📋 Binary check:")
    print(f"   telegram-bot-api: {'✅' if telegram_bot_api_path else '❌'}")
    
    if not telegram_bot_api_path:
        print("❌ telegram-bot-api binary not found")
        print("   Install it or run: docker-compose up telegram-bot-api")
        return False
    
    # Test binary
    try:
        import subprocess
        test_result = subprocess.run(
            [telegram_bot_api_path, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"📋 Binary test:")
        print(f"   Return code: {test_result.returncode}")
        if test_result.returncode == 0:
            print("   ✅ Binary works")
        else:
            print(f"   ❌ Binary error: {test_result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Binary test failed: {e}")
        return False
    
    # Test API endpoints
    print(f"📋 API endpoints test:")
    endpoints = [
        "http://localhost:8081/health",
        "http://localhost:8081/",
        "http://localhost:8081/bot"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"   {endpoint}: ✅ {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   {endpoint}: ❌ {e}")
    
    print("✅ Self-hosted Bot API test completed")
    return True

if __name__ == "__main__":
    success = test_self_hosted_api()
    sys.exit(0 if success else 1)
