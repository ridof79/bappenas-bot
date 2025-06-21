#!/bin/bash
# deploy.sh - Manual deployment script

set -e

echo "🚀 Starting deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/ubuntu/telegram-clock-bot"
SERVICE_NAME="telegram-clock-bot"
BACKUP_DIR="/home/ubuntu/backups"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo -e "${YELLOW}📦 Creating backup...${NC}"
timestamp=$(date +"%Y%m%d_%H%M%S")
cp $PROJECT_DIR/clock_bot.py $BACKUP_DIR/clock_bot_$timestamp.py
cp $PROJECT_DIR/attendance_data.json $BACKUP_DIR/attendance_data_$timestamp.json 2>/dev/null || echo "No attendance data to backup"

echo -e "${YELLOW}🔄 Pulling latest changes...${NC}"
cd $PROJECT_DIR
git pull origin main

echo -e "${YELLOW}🔧 Installing dependencies...${NC}"
source bot_env/bin/activate
pip install -r requirements.txt

echo -e "${YELLOW}✅ Testing bot syntax...${NC}"
python -m py_compile clock_bot.py

echo -e "${YELLOW}🔄 Restarting service...${NC}"
sudo systemctl restart $SERVICE_NAME

echo -e "${YELLOW}⏳ Waiting for service to start...${NC}"
sleep 5

echo -e "${YELLOW}📊 Checking service status...${NC}"
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Service is running successfully!${NC}"
    sudo systemctl status $SERVICE_NAME --no-pager -l
else
    echo -e "${RED}❌ Service failed to start!${NC}"
    echo -e "${YELLOW}📋 Recent logs:${NC}"
    sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${YELLOW}📋 Recent logs:${NC}"
sudo journalctl -u $SERVICE_NAME -n 5 --no-pager