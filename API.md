# Attendance Bot API Documentation

## Overview

Attendance Bot adalah bot Telegram yang menyediakan API untuk mengelola kehadiran anggota grup. Bot ini menggunakan python-telegram-bot library dan menyimpan data dalam SQLite database.

## Commands

### 1. Start Command
**Command:** `/start`

**Description:** Memulai bot dan menampilkan informasi fitur

**Response:**
```
👋 Selamat datang di Attendance Bot!

🤖 Saya adalah bot untuk mengelola kehadiran anggota grup.

📋 Fitur Utama:
• ⏰ Clock in/out otomatis dengan pengingat
• 📊 Laporan kehadiran harian
• ⚙️ Konfigurasi waktu yang fleksibel
• 📅 Pengaturan hari kerja

🔧 Perintah yang tersedia:
• /ping - Cek status bot
• /clockin - Clock in manual
• /clockout - Clock out manual
• /check - Cek kehadiran hari ini
• /status - Laporan kehadiran detail
• /config - Konfigurasi clock in/out
• /help - Bantuan penggunaan

💡 Tips: Tambahkan saya sebagai admin grup untuk fitur lengkap!
```

### 2. Ping Command
**Command:** `/ping`

**Description:** Mengecek status bot dan koneksi database

**Response:**
```
🟢 Bot aktif!
⏰ Waktu sekarang: 2024-01-15 10:30:00 (WIB)
💾 Database: Terhubung
```

### 3. Clock In Command
**Command:** `/clockin`

**Description:** Mencatat kehadiran (clock in) untuk user

**Requirements:**
- Hanya berfungsi di grup
- User belum clock in hari ini

**Response (Success):**
```
✅ John Doe berhasil clock in pada 08:30:15
```

**Response (Already Clocked In):**
```
⚠️ John Doe, Anda sudah clock in hari ini pada 08:30:15
```

### 4. Clock Out Command
**Command:** `/clockout`

**Description:** Mencatat kepulangan (clock out) untuk user

**Requirements:**
- Hanya berfungsi di grup
- User sudah clock in hari ini
- User belum clock out hari ini

**Response (Success):**
```
✅ John Doe berhasil clock out pada 17:30:45
```

**Response (Not Clocked In):**
```
⚠️ John Doe, Anda harus clock in terlebih dahulu!
```

### 5. Check Command
**Command:** `/check`

**Description:** Menampilkan status kehadiran hari ini

**Requirements:**
- Hanya berfungsi di grup

**Response:**
```
📊 Status Kehadiran Hari Ini

🟢 Clock In: 5 orang
🔴 Clock Out: 3 orang
📅 Tanggal: 15/01/2024
⏰ Waktu: 10:30:15
```

### 6. Status Command
**Command:** `/status`

**Description:** Menampilkan laporan kehadiran detail

**Requirements:**
- Hanya berfungsi di grup
- User harus admin

**Response:**
```
📊 Laporan Kehadiran - 15/01/2024

🟢 Clock In (5 orang):
• John Doe - 08:30:15
• Jane Smith - 08:45:20
• Bob Johnson - 09:00:10
• Alice Brown - 08:15:30
• Charlie Wilson - 08:55:45

🔴 Clock Out (3 orang):
• John Doe - 17:30:45
• Jane Smith - 17:45:20
• Bob Johnson - 17:15:10
```

### 7. Config Command
**Command:** `/config`

**Description:** Menu konfigurasi clock in/out

**Requirements:**
- Hanya berfungsi di grup
- User harus admin

**Response:** Menu interaktif dengan tombol:
- ⚙️ Konfigurasi Clock In
- ⚙️ Konfigurasi Clock Out
- 📊 Lihat Konfigurasi

### 8. Help Command
**Command:** `/help`

**Description:** Menampilkan bantuan penggunaan

**Response:**
```
📚 Bantuan Penggunaan Attendance Bot

🤖 Perintah Umum:
• /start - Memulai bot dan melihat fitur
• /ping - Cek status bot
• /help - Menampilkan bantuan ini

⏰ Perintah Clock In/Out:
• /clockin - Clock in manual
• /clockout - Clock out manual
• /check - Cek status kehadiran hari ini
• /status - Laporan kehadiran detail (Admin only)

⚙️ Perintah Konfigurasi (Admin only):
• /config - Menu konfigurasi clock in/out

📋 Cara Penggunaan:
1. Tambahkan bot sebagai admin grup
2. Atur konfigurasi dengan /config
3. Bot akan mengirim pengingat otomatis
4. Anggota dapat clock in/out manual atau otomatis

💡 Tips:
• Pastikan bot memiliki izin untuk mengirim pesan
• Konfigurasi hanya dapat diubah oleh admin
• Data kehadiran disimpan dalam database SQLite
```

## Callback Queries

### Configuration Callbacks

#### 1. Config Clock In
**Callback Data:** `config_clock_in`

**Description:** Menampilkan menu konfigurasi clock in

**Response:** Menu dengan tombol:
- 🕐 Waktu: 08:00 - 09:00
- ⏰ Interval: 15 menit
- 📅 Hari: Senin, Selasa, Rabu, Kamis, Jumat
- 💾 Simpan / ❌ Batal

#### 2. Config Clock Out
**Callback Data:** `config_clock_out`

**Description:** Menampilkan menu konfigurasi clock out

**Response:** Menu dengan tombol:
- 🕐 Waktu: 16:00 - 18:00
- ⏰ Interval: 15 menit
- 📅 Hari: Senin, Selasa, Rabu, Kamis, Jumat
- 💾 Simpan / ❌ Batal

#### 3. View Config
**Callback Data:** `view_config`

**Description:** Menampilkan konfigurasi saat ini

**Response:**
```
📊 Konfigurasi Saat Ini

⚙️ Konfigurasi Clock In

🕐 Waktu: 08:00 - 09:00
⏰ Interval Pengingat: 15 menit
📅 Hari Aktif: Senin, Selasa, Rabu, Kamis, Jumat

⚙️ Konfigurasi Clock Out

🕐 Waktu: 16:00 - 18:00
⏰ Interval Pengingat: 15 menit
📅 Hari Aktif: Senin, Selasa, Rabu, Kamis, Jumat
```

### Setup Callbacks

#### 1. Set Time
**Callback Data:** `set_clock_in_time` / `set_clock_out_time`

**Description:** Setup waktu clock in/out

**Response:**
```
🕐 Atur Waktu Clock In

Kirim waktu dalam format HH:MM
Contoh: 08:00 untuk jam 8 pagi

Format: START_TIME-END_TIME
Contoh: 08:00-09:00
```

#### 2. Set Interval
**Callback Data:** `set_clock_in_interval` / `set_clock_out_interval`

**Description:** Setup interval pengingat

**Response:**
```
⏰ Atur Interval Pengingat Clock In

Kirim interval dalam menit (1-1440)
Contoh: 15 untuk setiap 15 menit
```

#### 3. Set Days
**Callback Data:** `set_clock_in_days` / `set_clock_out_days`

**Description:** Setup hari kerja

**Response:** Menu dengan tombol untuk setiap hari:
- ✅ Senin
- ✅ Selasa
- ✅ Rabu
- ✅ Kamis
- ✅ Jumat
- ❌ Sabtu
- ❌ Minggu
- 💾 Simpan / ❌ Batal

### Day Selection Callbacks

#### Toggle Day
**Callback Data:** `day_clock_in_0` / `day_clock_out_1` (dll)

**Description:** Toggle hari aktif untuk konfigurasi

**Response:** Update menu dengan status hari yang berubah

### Save/Cancel Callbacks

#### 1. Save Configuration
**Callback Data:** `save_clock_in` / `save_clock_out`

**Description:** Menyimpan konfigurasi

**Response:** "✅ Konfigurasi berhasil disimpan!"

#### 2. Cancel Configuration
**Callback Data:** `cancel_config`

**Description:** Membatalkan konfigurasi

**Response:** "❌ Dibatalkan"

## Message Handling

### Text Input for Configuration

#### Time Input
**Format:** `HH:MM-HH:MM`

**Example:** `08:00-09:00`

**Validation:**
- Format harus HH:MM-HH:MM
- Jam: 00-23
- Menit: 00-59

**Response (Success):**
```
✅ Waktu Clock In berhasil diatur!
🕐 08:00 - 09:00
```

**Response (Error):**
```
❌ Format waktu tidak valid!
Gunakan format: START_TIME-END_TIME
Contoh: 08:00-09:00
```

#### Interval Input
**Format:** Integer (1-1440)

**Example:** `15`

**Validation:**
- Harus berupa angka
- Range: 1-1440 menit

**Response (Success):**
```
✅ Interval pengingat Clock In berhasil diatur!
⏰ Setiap 15 menit
```

**Response (Error):**
```
❌ Interval tidak valid!
Interval harus antara 1-1440 menit
```

## Database Schema

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    username TEXT,
    clock_type TEXT NOT NULL, -- 'in' atau 'out'
    clock_time DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chat_id, user_id, clock_type, DATE(clock_time))
);
```

### Configurations Table
```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    config_type TEXT NOT NULL, -- 'clock_in' atau 'clock_out'
    start_time TEXT NOT NULL, -- Format HH:MM
    end_time TEXT NOT NULL, -- Format HH:MM
    reminder_interval INTEGER NOT NULL, -- menit
    enabled_days TEXT NOT NULL, -- JSON array [0,1,2,3,4,5,6]
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chat_id, config_type)
);
```

### Chat Groups Table
```sql
CREATE TABLE chat_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE NOT NULL,
    chat_title TEXT,
    chat_type TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### Common Errors

#### 1. Bot Token Not Set
```
Error: Please set your bot token in environment variable BOT_TOKEN
```

#### 2. Database Error
```
Error: Error initializing database: [error details]
```

#### 3. Permission Error
```
⚠️ Hanya administrator yang dapat menggunakan perintah ini.
```

#### 4. Invalid Input
```
❌ Format waktu tidak valid!
Gunakan format HH:MM (contoh: 08:00)
```

#### 5. Already Clocked In/Out
```
⚠️ John Doe, Anda sudah clock in hari ini pada 08:30:15
```

## Scheduled Jobs

### Clock In Reminder
- **Frequency:** Setiap 5 menit
- **Function:** `send_clock_in_reminder`
- **Description:** Mengirim pengingat clock in untuk anggota yang belum hadir

### Clock Out Reminder
- **Frequency:** Setiap 5 menit
- **Function:** `send_clock_out_reminder`
- **Description:** Mengirim pengingat clock out untuk anggota yang belum pulang

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram bot token | - | Yes |
| `DATABASE_PATH` | Path to SQLite database | `attendance.db` | No |
| `TIMEZONE` | Timezone for bot | `Asia/Jakarta` | No |

## Rate Limits

- **Message Sending:** Sesuai dengan limit Telegram Bot API
- **Database Operations:** Tidak ada limit khusus
- **Scheduled Jobs:** Setiap 5 menit untuk reminder

## Security Considerations

1. **Bot Token:** Jangan pernah share bot token
2. **Admin Only:** Konfigurasi hanya untuk admin grup
3. **Input Validation:** Semua input divalidasi
4. **Database:** Gunakan SQLite dengan proper error handling
5. **Logging:** Log semua operasi penting

## Troubleshooting

### Bot Tidak Merespons
1. Cek bot token
2. Pastikan bot online
3. Cek log error

### Pengingat Tidak Muncul
1. Cek konfigurasi waktu
2. Pastikan hari kerja aktif
3. Cek permission bot

### Database Error
1. Cek file permission
2. Pastikan SQLite terinstall
3. Cek disk space 