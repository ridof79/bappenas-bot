#!/usr/bin/env python3
"""
Script untuk memeriksa struktur database yang sebenarnya
"""

import sqlite3

def check_database_structure():
    """Check the actual database structure"""
    print("=== Database Structure Check ===\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for (table_name,) in tables:
            print(f"  {table_name}")
        
        print()
        
        # Check structure of each table
        for (table_name,) in tables:
            print(f"=== Structure of table '{table_name}' ===")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  {col_name} ({col_type}) - PK: {pk}, Not Null: {not_null}")
            
            print()
            
            # Show sample data
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                sample_data = cursor.fetchall()
                if sample_data:
                    print(f"Sample data from '{table_name}':")
                    for row in sample_data:
                        print(f"  {row}")
                else:
                    print(f"No data in '{table_name}'")
                print()
            except Exception as e:
                print(f"Error reading data from {table_name}: {e}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def check_configurations_table():
    """Specifically check configurations table"""
    print("=== Configurations Table Check ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check if configurations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='configurations';")
        if not cursor.fetchone():
            print("❌ Configurations table does not exist!")
            return
        
        # Get all data from configurations
        cursor.execute("SELECT * FROM configurations;")
        configs = cursor.fetchall()
        
        if not configs:
            print("No configurations found in database")
        else:
            print("All configurations:")
            for config in configs:
                print(f"  {config}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    check_database_structure()
    check_configurations_table()

if __name__ == "__main__":
    main() 