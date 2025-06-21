#!/usr/bin/env python3
"""
Script untuk mengecek semua chat groups dan konfigurasinya
"""

import sqlite3
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.database import Database
from src.config.settings import Settings

def check_all_configurations():
    """Check semua chat groups dan konfigurasinya"""
    
    print("🔍 Checking All Chat Groups and Configurations")
    print("=" * 60)
    
    db = Database()
    
    # Get all chat groups
    chat_groups = db.get_all_chat_groups()
    print(f"📋 Found {len(chat_groups)} chat groups:")
    print()
    
    for i, group in enumerate(chat_groups, 1):
        chat_id = group['chat_id']
        chat_title = group['chat_title']
        chat_type = group['chat_type']
        created_at = group['created_at']
        
        print(f"{i}. 📱 **{chat_title}**")
        print(f"   🆔 Chat ID: {chat_id}")
        print(f"   📝 Type: {chat_type}")
        print(f"   📅 Created: {created_at}")
        
        # Check configurations for this chat
        clock_in_config = db.get_configuration(chat_id, 'clock_in')
        clock_out_config = db.get_configuration(chat_id, 'clock_out')
        
        print(f"   ⏰ Clock In: {'✅' if clock_in_config else '❌'}")
        if clock_in_config:
            print(f"      Time: {clock_in_config['start_time']}-{clock_in_config['end_time']}")
            print(f"      Interval: {clock_in_config['reminder_interval']}min")
            print(f"      Days: {clock_in_config['enabled_days']}")
        
        print(f"   🏠 Clock Out: {'✅' if clock_out_config else '❌'}")
        if clock_out_config:
            print(f"      Time: {clock_out_config['start_time']}-{clock_out_config['end_time']}")
            print(f"      Interval: {clock_out_config['reminder_interval']}min")
            print(f"      Days: {clock_out_config['enabled_days']}")
        
        print()
    
    # Get all configurations
    print("📊 All Configurations in Database:")
    print("-" * 40)
    
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, chat_id, config_type, start_time, end_time, 
                       reminder_interval, enabled_days, is_active, created_at, updated_at
                FROM configurations
                ORDER BY chat_id, config_type
            """)
            
            rows = cursor.fetchall()
            print(f"Total configurations: {len(rows)}")
            
            for row in rows:
                config_id, chat_id, config_type, start_time, end_time, interval, days_json, is_active, created_at, updated_at = row
                enabled_days = json.loads(days_json) if days_json else []
                
                print(f"  ({config_id}, {chat_id}, '{config_type}', '{start_time}', '{end_time}', {interval}, '{days_json}', {is_active}, '{created_at}', '{updated_at}')")
                print(f"    Enabled days: {enabled_days}")
                print()
    
    except Exception as e:
        print(f"❌ Error reading configurations: {e}")
    
    print("✅ Check completed!")

if __name__ == "__main__":
    check_all_configurations() 