# Attendance Bot - Telegram Bot untuk Manajemen Kehadiran

Bot Telegram yang dirancang untuk mengelola kehadiran anggota grup dengan fitur clock in/out otomatis, pengingat, dan laporan kehadiran.

## 🚀 Fitur Utama

### 1. Konfigurasi Clock In/Out
- **Batas waktu awal dan akhir** untuk clock in/out
- **Interval pengingat** yang dapat disesuaikan (setiap x menit)
- **Pengaturan hari kerja** (Senin-Jumat, atau hari lainnya)
- **Penyimpanan konfigurasi** dalam database SQLite

### 2. Sistem Kehadiran
- **Clock in/out manual** dengan perintah `/clockin` dan `/clockout`
- **Pencatatan otomatis** ke database SQLite
- **Validasi kehadiran** (harus clock in sebelum clock out)
- **Pencegahan duplikasi** (tidak bisa clock in/out dua kali dalam satu hari)

### 3. Pengingat Otomatis
- **Pengingat clock in** dengan mention anggota yang belum hadir
- **Pengingat clock out** dengan mention anggota yang belum pulang
- **Interval pengingat** yang dapat dikonfigurasi
- **Pengingat hanya pada hari kerja** yang ditentukan

### 4. Laporan dan Monitoring
- **Status kehadiran harian** dengan perintah `/check`
- **Laporan detail** dengan perintah `/status` (admin only)
- **Format laporan** yang mudah dibaca
- **Statistik kehadiran** per hari

### 5. Antarmuka Interaktif
- **Menu konfigurasi** dengan tombol interaktif
- **Setup waktu** dengan input teks yang mudah
- **Pemilihan hari kerja** dengan toggle button
- **Validasi input** yang user-friendly

## 📋 Persyaratan Sistem

- Python 3.8 atau lebih baru
- pip (Python package installer)
- Bot Token dari BotFather Telegram
- Akses internet untuk koneksi ke Telegram API

## 🛠️ Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd bappenas-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Buat file `.env` atau set environment variable:
```bash
export BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
export DATABASE_PATH="attendance.db"
```

### 4. Jalankan Bot
```bash
python main.py
```

## 🔧 Konfigurasi Bot

### 1. Dapatkan Bot Token
1. Buka Telegram dan cari `@BotFather`
2. Kirim perintah `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Salin token yang diberikan

### 2. Set Bot Token
```bash
export BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 3. Tambahkan Bot ke Grup
1. Tambahkan bot sebagai anggota grup
2. Berikan bot permission sebagai admin
3. Pastikan bot dapat mengirim pesan dan mention anggota

## 📖 Cara Penggunaan

### Perintah Dasar
- `/start` - Memulai bot dan melihat fitur
- `/ping` - Cek status bot
- `/help` - Bantuan penggunaan

### Perintah Clock In/Out
- `/clockin` - Clock in manual
- `/clockout` - Clock out manual
- `/check` - Cek status kehadiran hari ini
- `/status` - Laporan kehadiran detail (Admin only)

### Perintah Konfigurasi (Admin only)
- `/config` - Menu konfigurasi clock in/out

### Setup Konfigurasi
1. Jalankan `/config` di grup
2. Pilih "Konfigurasi Clock In" atau "Konfigurasi Clock Out"
3. Atur waktu, interval, dan hari kerja
4. Simpan konfigurasi

## 🗄️ Struktur Database

Bot menggunakan SQLite dengan 3 tabel utama:

### 1. Tabel `attendance`
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

### 2. Tabel `configurations`
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

### 3. Tabel `chat_groups`
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

## 📁 Struktur Proyek

```
bappenas-bot/
├── main.py                 # File utama bot
├── requirements.txt        # Dependencies
├── README.md              # Dokumentasi
├── src/                   # Source code
│   ├── __init__.py
│   ├── config/           # Konfigurasi
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── database/         # Database layer
│   │   ├── __init__.py
│   │   └── database.py
│   ├── handlers/         # Event handlers
│   │   ├── __init__.py
│   │   ├── command_handlers.py
│   │   ├── callback_handlers.py
│   │   └── message_handlers.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
└── attendance.db         # Database file (auto-generated)
```

## 🔄 Workflow Bot

### 1. Setup Awal
1. Admin menjalankan `/config`
2. Mengatur waktu clock in/out
3. Mengatur interval pengingat
4. Memilih hari kerja
5. Menyimpan konfigurasi

### 2. Operasi Harian
1. Bot memeriksa konfigurasi setiap 5 menit
2. Jika waktu sesuai, kirim pengingat
3. Mention anggota yang belum clock in/out
4. Anggota dapat clock in/out manual atau otomatis

### 3. Monitoring
1. Admin dapat cek status dengan `/check`
2. Laporan detail dengan `/status`
3. Data tersimpan dalam database SQLite

## 🚨 Troubleshooting

### Bot tidak merespons
- Periksa apakah bot token benar
- Pastikan bot memiliki permission admin
- Cek log untuk error messages

### Pengingat tidak muncul
- Periksa konfigurasi waktu
- Pastikan hari ini adalah hari kerja
- Cek apakah bot dapat mention anggota

### Database error
- Periksa permission file database
- Pastikan SQLite terinstall
- Cek log untuk error database

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 📞 Support

Jika Anda mengalami masalah atau memiliki pertanyaan:
1. Periksa dokumentasi ini
2. Cek log error
3. Buat issue di repository
4. Hubungi developer

## 🔮 Roadmap

- [ ] Export laporan ke Excel/PDF
- [ ] Dashboard web untuk monitoring
- [ ] Integrasi dengan sistem HR
- [ ] Notifikasi email/SMS
- [ ] Multi-language support
- [ ] Backup database otomatis
- [ ] Analytics dan statistik lanjutan
