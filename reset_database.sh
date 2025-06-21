#!/bin/bash

# Reset database script
# This will remove the old database and create a new one with correct schema

echo "🗑️ Resetting database..."

# Stop the bot service
echo "⏹️ Stopping bot service..."
sudo systemctl stop telegram-bot.service

# Backup old database if exists
if [ -f "data/attendance.db" ]; then
    echo "💾 Backing up old database..."
    cp data/attendance.db "data/attendance.db.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Remove old database
echo "🗑️ Removing old database..."
rm -f data/attendance.db

# Create new database by running the bot briefly
echo "🔄 Creating new database..."
cd /home/ubuntu/telegram-bappenas-bot
source bot_env/bin/activate

# Test database creation
python -c "
from src.database.database import Database
db = Database('data/attendance.db')
print('✅ Database created successfully')
"

# Start the bot service
echo "▶️ Starting bot service..."
sudo systemctl start telegram-bot.service

# Check status
echo "📊 Checking bot status..."
sudo systemctl status telegram-bot.service --no-pager

echo "✅ Database reset completed!"
echo "📝 Old database backed up as data/attendance.db.backup.*" 