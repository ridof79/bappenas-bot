#!/usr/bin/env python3
"""
Script untuk mengecek dan memperbaiki konfigurasi yang hilang
"""

import sqlite3
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import Database
from src.config.settings import Settings

def check_and_fix_configurations():
    """Check dan fix konfigurasi yang hilang"""
    
    print("🔍 Checking Database Configurations")
    print("=" * 50)
    
    db = Database()
    
    # Get all chat groups
    chat_groups = db.get_all_chat_groups()
    print(f"📋 Found {len(chat_groups)} chat groups:")
    
    for group in chat_groups:
        chat_id = group['chat_id']
        chat_title = group['chat_title']
        print(f"   - {chat_title} (ID: {chat_id})")
        
        # Check configurations for this chat
        clock_in_config = db.get_configuration(chat_id, 'clock_in')
        clock_out_config = db.get_configuration(chat_id, 'clock_out')
        
        print(f"     Clock In: {'✅' if clock_in_config else '❌'}")
        print(f"     Clock Out: {'✅' if clock_out_config else '❌'}")
        
        # Fix missing configurations
        if not clock_in_config:
            print(f"     🔧 Creating default clock_in config...")
            success = db.save_configuration(
                chat_id=chat_id,
                config_type='clock_in',
                start_time=Settings.DEFAULT_CLOCK_IN_START,
                end_time=Settings.DEFAULT_CLOCK_IN_END,
                reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                enabled_days=Settings.DEFAULT_ENABLED_DAYS
            )
            print(f"       {'✅ Success' if success else '❌ Failed'}")
        
        if not clock_out_config:
            print(f"     🔧 Creating default clock_out config...")
            success = db.save_configuration(
                chat_id=chat_id,
                config_type='clock_out',
                start_time=Settings.DEFAULT_CLOCK_OUT_START,
                end_time=Settings.DEFAULT_CLOCK_OUT_END,
                reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                enabled_days=Settings.DEFAULT_ENABLED_DAYS
            )
            print(f"       {'✅ Success' if success else '❌ Failed'}")
        
        print()
    
    # Show final count
    print("📊 Final Configuration Count:")
    all_configs = db.get_all_active_configurations()
    print(f"   Total configurations: {len(all_configs)}")
    
    for config in all_configs:
        print(f"   - {config['config_type']} for chat {config['chat_id']}")
    
    print("\n✅ Configuration check completed!")

if __name__ == "__main__":
    check_and_fix_configurations() 