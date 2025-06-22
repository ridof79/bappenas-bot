import sqlite3
import logging
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple
import json
import threading

logger = logging.getLogger(__name__)

class Database:
    _connection_pool = {}
    _lock = threading.Lock()

    # Configuration cache
    _config_cache = {}
    _cache_timeout = 300  # 5 minutes in seconds
    _last_cache_update = {}

    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a connection from the pool or create a new one"""
        thread_id = threading.get_ident()

        with self._lock:
            if thread_id not in self._connection_pool:
                conn = sqlite3.connect(self.db_path)
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                # Set journal mode to WAL for better concurrency
                conn.execute("PRAGMA journal_mode = WAL")
                # Set synchronous mode to NORMAL for better performance
                conn.execute("PRAGMA synchronous = NORMAL")
                self._connection_pool[thread_id] = conn

            return self._connection_pool[thread_id]

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

                # Create indexes for attendance table
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_chat_date ON attendance(chat_id, date_only)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_user ON attendance(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_type ON attendance(clock_type)')

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

                # Create indexes for configurations table
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_config_chat ON configurations(chat_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_config_active ON configurations(is_active)')

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

                # Create index for chat_groups table
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_groups_active ON chat_groups(is_active)')

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def add_chat_group(self, chat_id: int, chat_title: str, chat_type: str):
        """Add a chat group to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if chat group already exists
                cursor.execute('''
                    SELECT chat_id FROM chat_groups 
                    WHERE chat_id = ?
                ''', (chat_id,))

                existing = cursor.fetchone()

                if existing:
                    # Update existing chat group
                    cursor.execute('''
                        UPDATE chat_groups 
                        SET chat_title = ?, chat_type = ?
                        WHERE chat_id = ?
                    ''', (chat_title, chat_type, chat_id))
                    logger.info(f"✅ Chat group updated: ID={chat_id}, Title='{chat_title}', Type={chat_type}")
                else:
                    # Insert new chat group
                    cursor.execute('''
                        INSERT INTO chat_groups 
                        (chat_id, chat_title, chat_type, created_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (chat_id, chat_title, chat_type))
                    logger.info(f"✅ Chat group created: ID={chat_id}, Title='{chat_title}', Type={chat_type}")

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Error adding chat group to database: {e}")
            return False

    def record_attendance(self, chat_id: int, user_id: int, user_name: str, 
                         username: str, clock_type: str, clock_time: datetime):
        """Record attendance in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attendance 
                (chat_id, user_id, user_name, username, clock_type, clock_time, date_only)
                VALUES (?, ?, ?, ?, ?, ?, DATE(?))
            ''', (chat_id, user_id, user_name, username, clock_type, clock_time, clock_time))
            conn.commit()
            logger.info(f"✅ Attendance recorded: Chat={chat_id}, User={user_name}({user_id}), Type={clock_type}, Time={clock_time}")
            return True
        except sqlite3.IntegrityError as e:
            # Handle unique constraint violation (user already clocked in/out today)
            logger.warning(f"⚠️ User already recorded attendance: Chat={chat_id}, User={user_name}({user_id}), Type={clock_type}")
            return False
        except Exception as e:
            logger.error(f"❌ Error recording attendance: {e}")
            return False

    def get_today_attendance(self, chat_id: int, date: datetime) -> Dict:
        """Get attendance for a specific date"""
        try:
            conn = self.get_connection()
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
        except sqlite3.Error as e:
            logger.error(f"Database error getting today's attendance: {e}")
            return {'clock_in': {}, 'clock_out': {}}
        except Exception as e:
            logger.error(f"Error getting today's attendance: {e}")
            return {'clock_in': {}, 'clock_out': {}}

    def save_configuration(self, chat_id: int, config_type: str, start_time: str, 
                          end_time: str, reminder_interval: int, enabled_days: List[int]):
        """Save clock in/out configuration and invalidate cache"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if configuration already exists
            cursor.execute('''
                SELECT id FROM configurations 
                WHERE chat_id = ? AND config_type = ?
            ''', (chat_id, config_type))

            existing = cursor.fetchone()

            if existing:
                # Update existing configuration
                enabled_days_json = json.dumps(enabled_days)
                cursor.execute('''
                    UPDATE configurations 
                    SET start_time = ?, end_time = ?, reminder_interval = ?, 
                        enabled_days = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE chat_id = ? AND config_type = ?
                ''', (start_time, end_time, reminder_interval, enabled_days_json, chat_id, config_type))
                logger.info(f"✅ Configuration updated: Chat={chat_id}, Type={config_type}, Time={start_time}-{end_time}, Interval={reminder_interval}min, Days={enabled_days}")
            else:
                # Insert new configuration
                enabled_days_json = json.dumps(enabled_days)
                cursor.execute('''
                    INSERT INTO configurations 
                    (chat_id, config_type, start_time, end_time, reminder_interval, 
                     enabled_days, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (chat_id, config_type, start_time, end_time, reminder_interval, enabled_days_json))
                logger.info(f"✅ Configuration created: Chat={chat_id}, Type={config_type}, Time={start_time}-{end_time}, Interval={reminder_interval}min, Days={enabled_days}")

            conn.commit()

            # Invalidate cache for this configuration and all active configurations
            with self._lock:
                # Remove specific configuration from cache
                cache_key = f"{chat_id}_{config_type}"
                if cache_key in self._config_cache:
                    del self._config_cache[cache_key]
                    if cache_key in self._last_cache_update:
                        del self._last_cache_update[cache_key]

                # Remove all active configurations from cache
                if "all_active_configs" in self._config_cache:
                    del self._config_cache["all_active_configs"]
                    if "all_active_configs" in self._last_cache_update:
                        del self._last_cache_update["all_active_configs"]

            return True

        except sqlite3.Error as e:
            logger.error(f"❌ Database error saving configuration: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error saving configuration: {e}")
            return False

    def get_configuration(self, chat_id: int, config_type: str) -> Optional[Dict]:
        """Get configuration for a chat and type with caching"""
        import time

        # Create a cache key
        cache_key = f"{chat_id}_{config_type}"

        # Check if we have a valid cached configuration
        current_time = time.time()
        with self._lock:
            if (cache_key in self._config_cache and 
                current_time - self._last_cache_update.get(cache_key, 0) < self._cache_timeout):
                logger.debug(f"Using cached configuration for {cache_key}")
                return self._config_cache[cache_key]

        # If not in cache or expired, get from database
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT start_time, end_time, reminder_interval, enabled_days, is_active
                FROM configurations 
                WHERE chat_id = ? AND config_type = ?
            ''', (chat_id, config_type))

            result = cursor.fetchone()
            if result:
                start_time, end_time, reminder_interval, enabled_days_json, is_active = result
                config = {
                    'config_type': config_type,
                    'start_time': start_time,
                    'end_time': end_time,
                    'reminder_interval': reminder_interval,
                    'enabled_days': json.loads(enabled_days_json),
                    'is_active': bool(is_active)
                }

                # Update cache
                with self._lock:
                    self._config_cache[cache_key] = config
                    self._last_cache_update[cache_key] = current_time

                return config

            # If no configuration found, cache None result too to avoid repeated lookups
            with self._lock:
                self._config_cache[cache_key] = None
                self._last_cache_update[cache_key] = current_time

            return None

        except sqlite3.Error as e:
            logger.error(f"Database error getting configuration: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return None

    def get_all_active_configurations(self) -> List[Dict]:
        """Get all active configurations with caching"""
        import time

        # Cache key for all active configurations
        cache_key = "all_active_configs"

        # Check if we have a valid cached result
        current_time = time.time()
        with self._lock:
            if (cache_key in self._config_cache and 
                current_time - self._last_cache_update.get(cache_key, 0) < self._cache_timeout):
                logger.debug("Using cached active configurations")
                return self._config_cache[cache_key]

        # If not in cache or expired, get from database
        try:
            conn = self.get_connection()
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
                config = {
                    'chat_id': chat_id,
                    'config_type': config_type,
                    'start_time': start_time,
                    'end_time': end_time,
                    'reminder_interval': reminder_interval,
                    'enabled_days': json.loads(enabled_days_json)
                }
                configurations.append(config)

                # Also update individual configuration cache
                individual_cache_key = f"{chat_id}_{config_type}"
                with self._lock:
                    self._config_cache[individual_cache_key] = {
                        'config_type': config_type,
                        'start_time': start_time,
                        'end_time': end_time,
                        'reminder_interval': reminder_interval,
                        'enabled_days': json.loads(enabled_days_json),
                        'is_active': True
                    }
                    self._last_cache_update[individual_cache_key] = current_time

            # Update cache for all configurations
            with self._lock:
                self._config_cache[cache_key] = configurations
                self._last_cache_update[cache_key] = current_time

            return configurations

        except sqlite3.Error as e:
            logger.error(f"Database error getting all configurations: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting all configurations: {e}")
            return []

    def get_members_without_attendance(self, chat_id: int, clock_type: str, 
                                     date: datetime, member_ids: List[int]) -> List[int]:
        """Get member IDs who haven't clocked in/out on a specific date"""
        if not member_ids:
            return []

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            date_str = date.strftime('%Y-%m-%d')

            cursor.execute('''
                SELECT user_id FROM attendance 
                WHERE chat_id = ? AND clock_type = ? AND DATE(clock_time) = ?
            ''', (chat_id, clock_type, date_str))

            attended_user_ids = {row[0] for row in cursor.fetchall()}
            return [user_id for user_id in member_ids if user_id not in attended_user_ids]

        except sqlite3.Error as e:
            logger.error(f"Database error getting members without attendance: {e}")
            return member_ids
        except Exception as e:
            logger.error(f"Error getting members without attendance: {e}")
            return member_ids

    def get_all_chat_groups(self):
        """Get all chat groups"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT chat_id, chat_title, chat_type, created_at
                FROM chat_groups
                WHERE is_active = 1
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

        except sqlite3.Error as e:
            logger.error(f"Database error getting all chat groups: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting all chat groups: {e}")
            return []
