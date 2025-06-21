#!/bin/bash

# Setup script for Telegram Attendance Bot deployment
# Run this script on your EC2 server to setup the bot

set -e

echo "🚀 Setting up Telegram Attendance Bot..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    exit 1
fi

# Variables
BOT_DIR="/home/ubuntu/telegram-bappenas-bot"
SERVICE_NAME="telegram-bot.service"

# Create bot directory if not exists
if [ ! -d "$BOT_DIR" ]; then
    echo "📁 Creating bot directory..."
    mkdir -p "$BOT_DIR"
fi

cd "$BOT_DIR"

# Clone repository if not exists
if [ ! -d ".git" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/yourusername/bappenas-bot.git .
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "bot_env" ]; then
    python3 -m venv bot_env
fi

# Activate virtual environment and install dependencies
source bot_env/bin/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "📦 Installing default dependencies..."
    pip install python-telegram-bot[job-queue] pytz
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
chmod 755 data

# Setup systemd service
echo "⚙️ Setting up systemd service..."
if [ -f "telegram-bot.service" ]; then
    sudo cp telegram-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable telegram-bot.service
    echo "✅ Systemd service configured"
else
    echo "⚠️ telegram-bot.service file not found"
fi

# Create environment file if not exists
if [ ! -f ".env" ]; then
    echo "🔧 Creating environment file..."
    cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Database Configuration
DATABASE_PATH=data/attendance.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=data/bot.log
EOF
    echo "✅ Environment file created"
    echo "⚠️ Please update .env file with your bot token"
fi

# Create backup script
echo "💾 Creating backup script..."
cat > backup_db.sh << 'EOF'
#!/bin/bash
# Database backup script

BACKUP_DIR="data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/attendance_$DATE.db"

mkdir -p "$BACKUP_DIR"

if [ -f "data/attendance.db" ]; then
    cp data/attendance.db "$BACKUP_FILE"
    echo "✅ Database backed up to $BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/attendance_*.db | tail -n +11 | xargs -r rm
    echo "🧹 Old backups cleaned up"
else
    echo "⚠️ No database file found to backup"
fi
EOF

chmod +x backup_db.sh

# Create restore script
echo "🔄 Creating restore script..."
cat > restore_db.sh << 'EOF'
#!/bin/bash
# Database restore script

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la data/backups/attendance_*.db 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Restoring database from $BACKUP_FILE..."
cp "$BACKUP_FILE" data/attendance.db
echo "✅ Database restored successfully"
EOF

chmod +x restore_db.sh

# Create log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/telegram-bot > /dev/null << EOF
$BOT_DIR/data/bot.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload telegram-bot.service
    endscript
}
EOF

echo "✅ Log rotation configured"

# Final instructions
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your bot token:"
echo "   nano $BOT_DIR/.env"
echo ""
echo "2. Start the bot service:"
echo "   sudo systemctl start telegram-bot.service"
echo ""
echo "3. Check bot status:"
echo "   sudo systemctl status telegram-bot.service"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u telegram-bot.service -f"
echo ""
echo "5. Backup database:"
echo "   cd $BOT_DIR && ./backup_db.sh"
echo ""
echo "🔗 GitHub Actions will automatically deploy updates when you push to main branch"
echo "" 