#!/usr/bin/env python3
"""
Script to run Attendance Bot with environment variables from file
"""

import os
import sys
import logging
from pathlib import Path

def load_env_file(env_file_path):
    """Load environment variables from file"""
    if not os.path.exists(env_file_path):
        print(f"Environment file {env_file_path} not found.")
        print("Please create .env file based on env.example")
        return False
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    return True

def check_required_env():
    """Check if required environment variables are set"""
    required_vars = ['BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment")
        return False
    
    return True

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/bot.log')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function"""
    print("🤖 Attendance Bot - Environment Loader")
    print("=" * 40)
    
    # Load environment variables
    env_files = ['.env', 'env.example']
    env_loaded = False
    
    for env_file in env_files:
        if load_env_file(env_file):
            print(f"✅ Loaded environment from {env_file}")
            env_loaded = True
            break
    
    if not env_loaded:
        print("❌ No environment file found")
        print("Please create .env file based on env.example")
        return 1
    
    # Check required environment variables
    if not check_required_env():
        return 1
    
    # Setup logging
    setup_logging()
    
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    print("🚀 Starting Attendance Bot...")
    print(f"📁 Database: {os.getenv('DATABASE_PATH', 'attendance.db')}")
    print(f"🌍 Timezone: {os.getenv('TIMEZONE', 'Asia/Jakarta')}")
    print("=" * 40)
    
    try:
        # Import and run the bot
        from main import main as run_bot
        run_bot()
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 