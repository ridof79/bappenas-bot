#!/usr/bin/env python3
"""
Test script for Attendance Bot
"""

import unittest
import tempfile
import os
from datetime import datetime, time
from unittest.mock import Mock, patch

from src.database.database import Database
from src.config.settings import Settings
from src.utils.helpers import (
    get_current_time, parse_time_string, validate_configuration,
    get_enabled_days_display, format_attendance_report
)

class TestDatabase(unittest.TestCase):
    """Test database functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        self.temp_db.close()
        os.unlink(self.temp_db.name)
    
    def test_add_chat_group(self):
        """Test adding chat group"""
        self.db.add_chat_group(12345, "Test Group", "group")
        
        # Verify chat group was added
        # This would require additional methods to query the database
        # For now, we just test that no exception is raised
        self.assertTrue(True)
    
    def test_record_attendance(self):
        """Test recording attendance"""
        current_time = datetime.now()
        success = self.db.record_attendance(
            chat_id=12345,
            user_id=67890,
            user_name="Test User",
            username="testuser",
            clock_type="in",
            clock_time=current_time
        )
        
        self.assertTrue(success)
    
    def test_save_configuration(self):
        """Test saving configuration"""
        success = self.db.save_configuration(
            chat_id=12345,
            config_type="clock_in",
            start_time="08:00",
            end_time="09:00",
            reminder_interval=15,
            enabled_days=[0, 1, 2, 3, 4]
        )
        
        self.assertTrue(success)

class TestSettings(unittest.TestCase):
    """Test settings functionality"""
    
    def test_validate_time_format(self):
        """Test time format validation"""
        self.assertTrue(Settings.validate_time_format("08:00"))
        self.assertTrue(Settings.validate_time_format("23:59"))
        self.assertFalse(Settings.validate_time_format("25:00"))
        self.assertFalse(Settings.validate_time_format("08:60"))
        self.assertFalse(Settings.validate_time_format("invalid"))
    
    def test_validate_reminder_interval(self):
        """Test reminder interval validation"""
        self.assertTrue(Settings.validate_reminder_interval(1))
        self.assertTrue(Settings.validate_reminder_interval(15))
        self.assertTrue(Settings.validate_reminder_interval(1440))
        self.assertFalse(Settings.validate_reminder_interval(0))
        self.assertFalse(Settings.validate_reminder_interval(1441))
    
    def test_validate_enabled_days(self):
        """Test enabled days validation"""
        self.assertTrue(Settings.validate_enabled_days([0, 1, 2, 3, 4]))
        self.assertTrue(Settings.validate_enabled_days([6]))
        self.assertFalse(Settings.validate_enabled_days([7]))
        self.assertFalse(Settings.validate_enabled_days([-1]))
        self.assertFalse(Settings.validate_enabled_days([]))
    
    def test_get_day_name(self):
        """Test day name retrieval"""
        self.assertEqual(Settings.get_day_name(0), "Senin")
        self.assertEqual(Settings.get_day_name(6), "Minggu")
        self.assertEqual(Settings.get_day_name(7), "Day 7")

class TestHelpers(unittest.TestCase):
    """Test helper functions"""
    
    def test_parse_time_string(self):
        """Test time string parsing"""
        self.assertEqual(parse_time_string("08:00"), time(8, 0))
        self.assertEqual(parse_time_string("23:59"), time(23, 59))
        self.assertIsNone(parse_time_string("25:00"))
        self.assertIsNone(parse_time_string("invalid"))
    
    def test_get_enabled_days_display(self):
        """Test enabled days display"""
        days = [0, 1, 2]
        display = get_enabled_days_display(days)
        self.assertIn("Senin", display)
        self.assertIn("Selasa", display)
        self.assertIn("Rabu", display)
    
    def test_validate_configuration(self):
        """Test configuration validation"""
        errors = validate_configuration("08:00", "09:00", 15, [0, 1, 2, 3, 4])
        self.assertEqual(len(errors), 0)
        
        errors = validate_configuration("25:00", "09:00", 15, [0, 1, 2, 3, 4])
        self.assertIn("start_time", errors)
        
        errors = validate_configuration("08:00", "09:00", 0, [0, 1, 2, 3, 4])
        self.assertIn("reminder_interval", errors)
    
    def test_format_attendance_report(self):
        """Test attendance report formatting"""
        attendance_data = {
            'clock_in': {
                '123': {'name': 'User 1', 'time': '08:00'},
                '456': {'name': 'User 2', 'time': '08:30'}
            },
            'clock_out': {
                '123': {'name': 'User 1', 'time': '17:00'}
            }
        }
        
        date = datetime.now()
        report = format_attendance_report(attendance_data, date)
        
        self.assertIn("Clock In (2 orang)", report)
        self.assertIn("Clock Out (1 orang)", report)
        self.assertIn("User 1", report)
        self.assertIn("User 2", report)

class TestBotIntegration(unittest.TestCase):
    """Test bot integration"""
    
    @patch('src.config.settings.Settings.BOT_TOKEN', 'test_token')
    def test_bot_initialization(self):
        """Test bot initialization"""
        # This test would require mocking the telegram library
        # For now, we just test that the settings are accessible
        self.assertEqual(Settings.BOT_TOKEN, 'test_token')

def run_tests():
    """Run all tests"""
    print("Running Attendance Bot Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDatabase))
    test_suite.addTest(unittest.makeSuite(TestSettings))
    test_suite.addTest(unittest.makeSuite(TestHelpers))
    test_suite.addTest(unittest.makeSuite(TestBotIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 