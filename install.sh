#!/bin/bash

# Check if root user
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

# Update package lists
apt-get update -y

# Install necessary packages
apt-get install -y python3 python3-pip python3-venv git unrar 

# Install MongoDB (if needed)
# You might need to adjust this based on your MongoDB setup
# apt-get install -y mongodb-server

# Install python-dotenv
pip3 install python-dotenv 

# Create a project directory
mkdir -p nadiup-bot
cd nadiup-bot

# Clone the bot repository
git clone YOUR_BOT_REPOSITORY_URL .

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (replace placeholders)
echo "API_ID=YOUR_API_ID" > .env
echo "API_HASH=YOUR_API_HASH" >> .env
echo "BOT_TOKEN=YOUR_BOT_TOKEN" >> .env
echo "DATABASE_URL=YOUR_MONGODB_URL" >> .env # If you're using MongoDB
echo "DOWNLOAD_LOCATION=/path/to/your/download/folder" >> .env

# Install additional system dependencies (if required)
# Example:
# apt-get install -y libgdiplus

echo "Installation complete. Start the bot with:"
echo "python3 bot.py"
