#!/usr/bin/env python3
"""
Script untuk menambahkan konfigurasi clock_out ke database
"""

import sqlite3
from datetime import datetime

def add_clockout_config():
    """Add clock_out configuration to database"""
    print("=== Adding Clock Out Configuration ===\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Get chat ID from user
        chat_id = input("Masukkan Chat ID grup (contoh: -1001234567890): ").strip()
        
        if not chat_id:
            print("❌ Chat ID tidak boleh kosong")
            return
        
        try:
            chat_id = int(chat_id)
        except ValueError:
            print("❌ Chat ID harus berupa angka")
            return
        
        # Check if configuration already exists
        cursor.execute("SELECT * FROM configurations WHERE chat_id = ? AND config_type = 'clock_out'", (chat_id,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️ Konfigurasi clock_out sudah ada untuk chat {chat_id}")
            print(f"Konfigurasi: {existing}")
            
            update = input("Apakah ingin update konfigurasi? (y/n): ").strip().lower()
            if update != 'y':
                print("Konfigurasi tidak diubah")
                return
        
        # Get configuration details
        print("\nMasukkan konfigurasi clock out:")
        time_str = input("Waktu (format HH:MM, contoh: 17:00): ").strip()
        interval = input("Interval pengingat dalam menit (contoh: 30): ").strip()
        enabled = input("Aktifkan pengingat? (y/n): ").strip().lower()
        
        # Validate input
        if not time_str or not interval:
            print("❌ Waktu dan interval harus diisi")
            return
        
        try:
            # Validate time format
            datetime.strptime(time_str, '%H:%M')
            interval = int(interval)
        except ValueError:
            print("❌ Format waktu atau interval tidak valid")
            return
        
        enabled_bool = 1 if enabled == 'y' else 0
        
        # Insert or update configuration
        if existing:
            cursor.execute("""
                UPDATE configurations 
                SET time = ?, interval_minutes = ?, enabled = ?, updated_at = ?
                WHERE chat_id = ? AND config_type = 'clock_out'
            """, (time_str, interval, enabled_bool, datetime.now(), chat_id))
            print("✅ Konfigurasi clock_out berhasil diupdate")
        else:
            cursor.execute("""
                INSERT INTO configurations (chat_id, config_type, time, interval_minutes, enabled, created_at, updated_at)
                VALUES (?, 'clock_out', ?, ?, ?, ?, ?)
            """, (chat_id, time_str, interval, enabled_bool, datetime.now(), datetime.now()))
            print("✅ Konfigurasi clock_out berhasil ditambahkan")
        
        # Commit changes
        conn.commit()
        
        # Show the configuration
        cursor.execute("SELECT * FROM configurations WHERE chat_id = ? AND config_type = 'clock_out'", (chat_id,))
        config = cursor.fetchone()
        print(f"\nKonfigurasi saat ini: {config}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def show_all_configs():
    """Show all configurations in database"""
    print("\n=== All Configurations ===\n")
    
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM configurations ORDER BY chat_id, config_type")
        configs = cursor.fetchall()
        
        if not configs:
            print("Tidak ada konfigurasi di database")
        else:
            for config in configs:
                print(f"Chat ID: {config[1]}, Type: {config[2]}, Time: {config[3]}, Interval: {config[4]}min, Enabled: {config[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    print("Clock Out Configuration Manager\n")
    print("1. Tambah/Update konfigurasi clock_out")
    print("2. Lihat semua konfigurasi")
    print("3. Keluar")
    
    choice = input("\nPilih opsi (1-3): ").strip()
    
    if choice == '1':
        add_clockout_config()
    elif choice == '2':
        show_all_configs()
    elif choice == '3':
        print("Keluar...")
    else:
        print("Pilihan tidak valid")

if __name__ == "__main__":
    main() 