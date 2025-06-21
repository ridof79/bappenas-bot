#!/usr/bin/env python3
"""
Script untuk memperbaiki konfigurasi yang hilang
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import Database
from src.config.settings import Settings

def fix_missing_configurations():
    """Fix konfigurasi yang hilang untuk semua chat groups"""
    
    print("🔧 Fixing Missing Configurations")
    print("=" * 50)
    
    db = Database()
    
    # Get all chat groups
    chat_groups = db.get_all_chat_groups()
    print(f"📋 Found {len(chat_groups)} chat groups")
    
    total_fixed = 0
    
    for group in chat_groups:
        chat_id = group['chat_id']
        chat_title = group['chat_title']
        
        print(f"\n📱 Processing: {chat_title} (ID: {chat_id})")
        
        # Check and fix clock_in config
        clock_in_config = db.get_configuration(chat_id, 'clock_in')
        if not clock_in_config:
            print(f"   🔧 Creating clock_in config...")
            success = db.save_configuration(
                chat_id=chat_id,
                config_type='clock_in',
                start_time=Settings.DEFAULT_CLOCK_IN_START,
                end_time=Settings.DEFAULT_CLOCK_IN_END,
                reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                enabled_days=Settings.DEFAULT_ENABLED_DAYS
            )
            if success:
                print(f"   ✅ Clock_in config created")
                total_fixed += 1
            else:
                print(f"   ❌ Failed to create clock_in config")
        else:
            print(f"   ✅ Clock_in config exists")
        
        # Check and fix clock_out config
        clock_out_config = db.get_configuration(chat_id, 'clock_out')
        if not clock_out_config:
            print(f"   🔧 Creating clock_out config...")
            success = db.save_configuration(
                chat_id=chat_id,
                config_type='clock_out',
                start_time=Settings.DEFAULT_CLOCK_OUT_START,
                end_time=Settings.DEFAULT_CLOCK_OUT_END,
                reminder_interval=Settings.DEFAULT_REMINDER_INTERVAL,
                enabled_days=Settings.DEFAULT_ENABLED_DAYS
            )
            if success:
                print(f"   ✅ Clock_out config created")
                total_fixed += 1
            else:
                print(f"   ❌ Failed to create clock_out config")
        else:
            print(f"   ✅ Clock_out config exists")
    
    # Show final result
    print(f"\n📊 Summary:")
    print(f"   Total chat groups: {len(chat_groups)}")
    print(f"   Configurations fixed: {total_fixed}")
    
    # Count total configurations
    all_configs = db.get_all_active_configurations()
    print(f"   Total configurations now: {len(all_configs)}")
    
    print(f"\n✅ Fix completed!")

if __name__ == "__main__":
    fix_missing_configurations() 