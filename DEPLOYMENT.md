# Deployment Guide

## Overview
This guide explains how to deploy the Telegram Attendance Bot to your EC2 server using GitHub Actions.

## Prerequisites

### 1. EC2 Server Setup
- Ubuntu 20.04+ server
- Python 3.8+
- Git installed
- Self-hosted GitHub Actions runner configured

### 2. GitHub Repository Setup
- Repository with your bot code
- GitHub Secrets configured:
  - `BOT_TOKEN`: Your Telegram bot token
  - `TELEGRAM_NOTIFY_TOKEN`: Bot token for deployment notifications
  - `TELEGRAM_CHAT_ID`: Chat ID for deployment notifications

## Quick Setup

### Option 1: Automated Setup (Recommended)
1. SSH into your EC2 server
2. Run the setup script:
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/bappenas-bot/main/setup_deployment.sh | bash
```

### Option 2: Manual Setup
1. Clone the repository:
```bash
cd /home/ubuntu
git clone https://github.com/yourusername/bappenas-bot.git telegram-bappenas-bot
cd telegram-bappenas-bot
```

2. Create virtual environment:
```bash
python3 -m venv bot_env
source bot_env/bin/activate
pip install -r requirements.txt
```

3. Setup systemd service:
```bash
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot.service
```

4. Create data directory:
```bash
mkdir -p data
chmod 755 data
```

## Configuration

### 1. Environment Variables
Create `.env` file in the bot directory:
```bash
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Database Configuration
DATABASE_PATH=data/attendance.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=data/bot.log
```

### 2. Systemd Service
The service file `telegram-bot.service` is already configured with:
- Automatic restart on failure
- Proper logging
- Security restrictions
- Working directory setup

## GitHub Actions Workflow

The `.github/workflows/deploy.yml` file handles:
- Automatic deployment on push to main branch
- Database backup before deployment
- Dependency installation
- Service restart
- Health checks
- Deployment notifications

### Workflow Steps:
1. **Pull Changes**: Gets latest code from main branch
2. **Backup Database**: Creates backup before deployment
3. **Install Dependencies**: Updates Python packages
4. **Create Data Directory**: Ensures data directory exists
5. **Update Service**: Copies updated systemd service file
6. **Restart Service**: Restarts the bot with new code
7. **Health Check**: Verifies bot is running properly
8. **Notification**: Sends deployment status to Telegram

## Management Commands

### Start/Stop Bot
```bash
# Start bot
sudo systemctl start telegram-bot.service

# Stop bot
sudo systemctl stop telegram-bot.service

# Restart bot
sudo systemctl restart telegram-bot.service

# Check status
sudo systemctl status telegram-bot.service
```

### View Logs
```bash
# View real-time logs
sudo journalctl -u telegram-bot.service -f

# View recent logs
sudo journalctl -u telegram-bot.service -n 50

# View logs for specific date
sudo journalctl -u telegram-bot.service --since "2024-01-01"
```

### Database Management
```bash
# Backup database
./backup_db.sh

# Restore database
./restore_db.sh data/backups/attendance_20240101_120000.db

# View database size
ls -lh data/attendance.db
```

### Manual Deployment
```bash
# Pull latest changes
git pull origin main

# Install dependencies
source bot_env/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart telegram-bot.service
```

## Monitoring

### Health Checks
The deployment workflow includes health checks:
- Service status verification
- Log analysis for errors
- Database connectivity test

### Log Rotation
Logs are automatically rotated:
- Daily rotation
- 7 days retention
- Compression enabled

### Backup Strategy
- Automatic backup before each deployment
- Manual backup script available
- 10 backup files retention

## Troubleshooting

### Common Issues

1. **Bot not starting**
```bash
# Check service status
sudo systemctl status telegram-bot.service

# View detailed logs
sudo journalctl -u telegram-bot.service -n 100
```

2. **Permission issues**
```bash
# Fix data directory permissions
sudo chown -R ubuntu:ubuntu data/
chmod 755 data/
```

3. **Database issues**
```bash
# Check database file
ls -la data/attendance.db

# Restore from backup if needed
./restore_db.sh data/backups/attendance_YYYYMMDD_HHMMSS.db
```

4. **Dependencies issues**
```bash
# Reinstall dependencies
source bot_env/bin/activate
pip install --force-reinstall -r requirements.txt
```

### Emergency Recovery
```bash
# Stop bot
sudo systemctl stop telegram-bot.service

# Restore from backup
./restore_db.sh data/backups/attendance_YYYYMMDD_HHMMSS.db

# Start bot
sudo systemctl start telegram-bot.service
```

## Security Considerations

1. **File Permissions**: Data directory is restricted to ubuntu user
2. **Service Isolation**: Bot runs with limited privileges
3. **Log Security**: Logs are rotated and compressed
4. **Backup Security**: Backups are stored locally with proper permissions

## Performance Optimization

1. **Database**: SQLite is optimized for concurrent reads
2. **Memory**: Bot uses minimal memory footprint
3. **CPU**: Efficient async operations
4. **Storage**: Log rotation prevents disk space issues

## Support

For issues with deployment:
1. Check the logs first
2. Verify configuration files
3. Test manually before automated deployment
4. Use backup/restore scripts if needed 