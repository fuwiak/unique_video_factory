#!/usr/bin/env python3
"""
Setup script for self-hosted Bot API server
This script configures a self-hosted Bot API server to remove 20MB file size limits
"""

import os
import subprocess
import requests
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfHostedAPISetup:
    """Setup and manage self-hosted Bot API server"""
    
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.server_port = int(os.getenv('BOT_API_PORT', '8081'))
        self.server_url = f"http://localhost:{self.server_port}"
        
    def check_requirements(self):
        """Check if all required environment variables are set"""
        required_vars = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_BOT_TOKEN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.info("Please set the following variables:")
            logger.info("TELEGRAM_API_ID - Your Telegram API ID")
            logger.info("TELEGRAM_API_HASH - Your Telegram API Hash")
            logger.info("TELEGRAM_BOT_TOKEN - Your Bot Token")
            return False
        
        logger.info("✅ All required environment variables are set")
        return True
    
    def download_bot_api_server(self):
        """Download the official Bot API server binary"""
        try:
            logger.info("📥 Downloading Bot API server...")
            
            # Create directory for Bot API server
            api_dir = Path("bot_api_server")
            api_dir.mkdir(exist_ok=True)
            
            # Download URL for Bot API server (Linux x64)
            download_url = "https://github.com/tdlib/telegram-bot-api/releases/latest/download/telegram-bot-api"
            
            # Download using curl
            result = subprocess.run([
                "curl", "-L", "-o", str(api_dir / "telegram-bot-api"), download_url
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Make executable
                subprocess.run(["chmod", "+x", str(api_dir / "telegram-bot-api")])
                logger.info("✅ Bot API server downloaded successfully")
                return str(api_dir / "telegram-bot-api")
            else:
                logger.error(f"❌ Failed to download Bot API server: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error downloading Bot API server: {e}")
            return None
    
    def start_bot_api_server(self, server_path):
        """Start the Bot API server"""
        try:
            logger.info("🚀 Starting Bot API server...")
            
            # Server configuration
            server_args = [
                server_path,
                "--api-id", self.api_id,
                "--api-hash", self.api_hash,
                "--local",
                "--http-port", str(self.server_port),
                "--log-level", "1"
            ]
            
            # Start server in background
            process = subprocess.Popen(
                server_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is running
            if self.check_server_health():
                logger.info(f"✅ Bot API server started on port {self.server_port}")
                return process
            else:
                logger.error("❌ Bot API server failed to start")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error starting Bot API server: {e}")
            return None
    
    def check_server_health(self):
        """Check if the Bot API server is running"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def configure_bot_for_self_hosted(self):
        """Configure the bot to use self-hosted API"""
        try:
            logger.info("🔧 Configuring bot for self-hosted API...")
            
            # Update environment variables
            env_file = Path(".env")
            if env_file.exists():
                # Read current .env
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Update or add self-hosted API settings
                lines = content.split('\n')
                updated_lines = []
                
                # Remove old settings
                for line in lines:
                    if not line.startswith(('USE_SELF_HOSTED_API=', 'SELF_HOSTED_API_URL=')):
                        updated_lines.append(line)
                
                # Add new settings
                updated_lines.extend([
                    f"USE_SELF_HOSTED_API=true",
                    f"SELF_HOSTED_API_URL={self.server_url}",
                    f"MAX_FILE_SIZE_MB=2000"
                ])
                
                # Write updated .env
                with open(env_file, 'w') as f:
                    f.write('\n'.join(updated_lines))
                
                logger.info("✅ Bot configured for self-hosted API")
                return True
            else:
                logger.error("❌ .env file not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error configuring bot: {e}")
            return False
    
    def setup(self):
        """Main setup function"""
        logger.info("🚀 Setting up self-hosted Bot API server...")
        
        # Check requirements
        if not self.check_requirements():
            return False
        
        # Download Bot API server
        server_path = self.download_bot_api_server()
        if not server_path:
            return False
        
        # Start server
        server_process = self.start_bot_api_server(server_path)
        if not server_process:
            return False
        
        # Configure bot
        if not self.configure_bot_for_self_hosted():
            return False
        
        logger.info("✅ Self-hosted Bot API setup completed!")
        logger.info(f"🌐 Server URL: {self.server_url}")
        logger.info("📁 File size limit: 2GB (2000MB)")
        logger.info("🔄 Restart your bot to use the new configuration")
        
        return True

def main():
    """Main function"""
    setup = SelfHostedAPISetup()
    success = setup.setup()
    
    if success:
        print("\n🎉 Self-hosted Bot API setup completed successfully!")
        print("📋 Next steps:")
        print("1. Restart your bot")
        print("2. Test with large files (>20MB)")
        print("3. Enjoy unlimited file sizes!")
    else:
        print("\n❌ Setup failed. Please check the logs above.")
        print("💡 Make sure you have:")
        print("- TELEGRAM_API_ID")
        print("- TELEGRAM_API_HASH") 
        print("- TELEGRAM_BOT_TOKEN")

if __name__ == "__main__":
    main()
