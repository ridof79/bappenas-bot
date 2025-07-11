import os
import pytz
from typing import Dict, Any, Union
from pytz import timezone

class Settings:
    """Application settings and configuration"""

    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')

    # Timezone Configuration
    TIMEZONE = pytz.timezone('Asia/Jakarta')  # Default to Jakarta timezone

    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'attendance.db')

    @classmethod
    def validate_bot_token(cls):
        """Validate that the bot token is set and has the correct format"""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "Bot token is not set. Please set the BOT_TOKEN environment variable."
            )

        # Basic format validation (should be digits:alphanumeric)
        import re
        if not re.match(r'^\d+:[A-Za-z0-9_-]+$', cls.BOT_TOKEN):
            raise ValueError(
                "Bot token has invalid format. It should be in the format 'digits:alphanumeric'."
            )

        return True

    # Default Configuration Values
    DEFAULT_CLOCK_IN_START = "07:00"
    DEFAULT_CLOCK_IN_END = "09:00"
    DEFAULT_CLOCK_OUT_START = "16:00"
    DEFAULT_CLOCK_OUT_END = "18:00"
    DEFAULT_REMINDER_INTERVAL = 15  # minutes
    DEFAULT_ENABLED_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday

    # Day names for display
    DAY_NAMES = {
        0: "Senin",
        1: "Selasa", 
        2: "Rabu",
        3: "Kamis",
        4: "Jumat",
        5: "Sabtu",
        6: "Minggu"
    }

    # Clock types
    CLOCK_TYPES = {
        'clock_in': 'Clock In',
        'clock_out': 'Clock Out'
    }

    # Bot commands
    COMMANDS = {
        'start': 'Mulai bot',
        'ping': 'Cek status bot',
        'clockin': 'Clock in manual',
        'clockout': 'Clock out manual',
        'check': 'Cek kehadiran hari ini',
        'status': 'Laporan kehadiran detail',
        'config': 'Konfigurasi clock in/out',
        'help': 'Bantuan penggunaan bot'
    }

    @classmethod
    def get_timezone(cls) -> Any:
        """Get configured timezone"""
        return cls.TIMEZONE

    @classmethod
    def get_day_name(cls, day_number: int) -> str:
        """Get day name from day number"""
        return cls.DAY_NAMES.get(day_number, f"Day {day_number}")

    @classmethod
    def get_clock_type_name(cls, clock_type: str) -> str:
        """Get clock type display name"""
        return cls.CLOCK_TYPES.get(clock_type, clock_type)

    @classmethod
    def validate_time_format(cls, time_str: str) -> bool:
        """Validate time format HH:MM"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    @classmethod
    def validate_reminder_interval(cls, interval: int) -> bool:
        """Validate reminder interval in minutes"""
        return 1 <= interval <= 1440  # 1 minute to 24 hours

    @classmethod
    def validate_enabled_days(cls, days: list) -> bool:
        """Validate enabled days list"""
        return all(0 <= day <= 6 for day in days) and len(days) > 0 
