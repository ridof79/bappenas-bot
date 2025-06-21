import sqlite3
import logging
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create attendance table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        user_name TEXT NOT NULL,
                        username TEXT,
                        clock_type TEXT NOT NULL, -- 'in' or 'out'
                        clock_time DATETIME NOT NULL,
                        date_only TEXT NOT NULL, -- YYYY-MM-DD format for unique constraint
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(chat_id, user_id, clock_type, date_only)
                    )
                ''')
                
                # Create configuration table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configurations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,
                        config_type TEXT NOT NULL, -- 'clock_in' or 'clock_out'
                        start_time TEXT NOT NULL, -- HH:MM format
                        end_time TEXT NOT NULL, -- HH:MM format
                        reminder_interval INTEGER NOT NULL, -- minutes
                        enabled_days TEXT NOT NULL, -- JSON array of days [0,1,2,3,4,5,6]
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(chat_id, config_type)
                    )
                ''')
                
                # Create chat groups table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER UNIQUE NOT NULL,
                        chat_title TEXT,
                        chat_type TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_chat_group(self, chat_id: int, chat_title: str, chat_type: str):
        """Add or update chat group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO chat_groups (chat_id, chat_title, chat_type)
                    VALUES (?, ?, ?)
                ''', (chat_id, chat_title, chat_type))
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding chat group: {e}")
    
    def record_attendance(self, chat_id: int, user_id: int, user_name: str, 
                         username: str, clock_type: str, clock_time: datetime):
        """Record clock in/out attendance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                date_only = clock_time.strftime('%Y-%m-%d')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO attendance 
                    (chat_id, user_id, user_name, username, clock_type, clock_time, date_only)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (chat_id, user_id, user_name, username, clock_type, clock_time, date_only))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error recording attendance: {e}")
            return False
    
    def get_today_attendance(self, chat_id: int, date: datetime) -> Dict:
        """Get attendance for a specific date"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                date_str = date.strftime('%Y-%m-%d')
                
                cursor.execute('''
                    SELECT user_id, user_name, username, clock_type, clock_time
                    FROM attendance 
                    WHERE chat_id = ? AND DATE(clock_time) = ?
                    ORDER BY clock_time
                ''', (chat_id, date_str))
                
                results = cursor.fetchall()
                attendance = {'clock_in': {}, 'clock_out': {}}
                
                for row in results:
                    user_id, user_name, username, clock_type, clock_time = row
                    if clock_type == 'in':
                        attendance['clock_in'][str(user_id)] = {
                            'name': user_name,
                            'username': username,
                            'time': clock_time
                        }
                    else:
                        attendance['clock_out'][str(user_id)] = {
                            'name': user_name,
                            'username': username,
                            'time': clock_time
                        }
                
                return attendance
        except Exception as e:
            logger.error(f"Error getting today's attendance: {e}")
            return {'clock_in': {}, 'clock_out': {}}
    
    def save_configuration(self, chat_id: int, config_type: str, start_time: str, 
                          end_time: str, reminder_interval: int, enabled_days: List[int]):
        """Save clock in/out configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                enabled_days_json = json.dumps(enabled_days)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO configurations 
                    (chat_id, config_type, start_time, end_time, reminder_interval, 
                     enabled_days, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (chat_id, config_type, start_time, end_time, reminder_interval, enabled_days_json))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_configuration(self, chat_id: int, config_type: str) -> Optional[Dict]:
        """Get configuration for a chat and type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT start_time, end_time, reminder_interval, enabled_days, is_active
                    FROM configurations 
                    WHERE chat_id = ? AND config_type = ?
                ''', (chat_id, config_type))
                
                result = cursor.fetchone()
                if result:
                    start_time, end_time, reminder_interval, enabled_days_json, is_active = result
                    return {
                        'config_type': config_type,
                        'start_time': start_time,
                        'end_time': end_time,
                        'reminder_interval': reminder_interval,
                        'enabled_days': json.loads(enabled_days_json),
                        'is_active': bool(is_active)
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return None
    
    def get_all_active_configurations(self) -> List[Dict]:
        """Get all active configurations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT chat_id, config_type, start_time, end_time, 
                           reminder_interval, enabled_days
                    FROM configurations 
                    WHERE is_active = 1
                ''')
                
                results = cursor.fetchall()
                configurations = []
                
                for row in results:
                    chat_id, config_type, start_time, end_time, reminder_interval, enabled_days_json = row
                    configurations.append({
                        'chat_id': chat_id,
                        'config_type': config_type,
                        'start_time': start_time,
                        'end_time': end_time,
                        'reminder_interval': reminder_interval,
                        'enabled_days': json.loads(enabled_days_json)
                    })
                
                return configurations
        except Exception as e:
            logger.error(f"Error getting all configurations: {e}")
            return []
    
    def get_members_without_attendance(self, chat_id: int, clock_type: str, 
                                     date: datetime, member_ids: List[int]) -> List[int]:
        """Get member IDs who haven't clocked in/out on a specific date"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                date_str = date.strftime('%Y-%m-%d')
                
                cursor.execute('''
                    SELECT user_id FROM attendance 
                    WHERE chat_id = ? AND clock_type = ? AND DATE(clock_time) = ?
                ''', (chat_id, clock_type, date_str))
                
                attended_user_ids = {row[0] for row in cursor.fetchall()}
                return [user_id for user_id in member_ids if user_id not in attended_user_ids]
        except Exception as e:
            logger.error(f"Error getting members without attendance: {e}")
            return member_ids
    
    def get_all_chat_groups(self):
        """Get all chat groups"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT chat_id, chat_title, chat_type, created_at
                    FROM chat_groups
                    ORDER BY created_at DESC
                """)
                
                rows = cursor.fetchall()
                chat_groups = []
                
                for row in rows:
                    chat_groups.append({
                        'chat_id': row[0],
                        'chat_title': row[1],
                        'chat_type': row[2],
                        'created_at': row[3]
                    })
                
                return chat_groups
                
        except Exception as e:
            logger.error(f"Error getting all chat groups: {e}")
            return []
    
    def get_all_active_configurations(self):
        """Get all active configurations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT chat_id, config_type, start_time, end_time, 
                           reminder_interval, enabled_days, created_at, updated_at
                    FROM configurations
                    ORDER BY updated_at DESC
                """)
                
                rows = cursor.fetchall()
                configurations = []
                
                for row in rows:
                    configurations.append({
                        'chat_id': row[0],
                        'config_type': row[1],
                        'start_time': row[2],
                        'end_time': row[3],
                        'reminder_interval': row[4],
                        'enabled_days': json.loads(row[5]) if row[5] else [],
                        'created_at': row[6],
                        'updated_at': row[7]
                    })
                
                return configurations
                
        except Exception as e:
            logger.error(f"Error getting all active configurations: {e}")
            return [] 