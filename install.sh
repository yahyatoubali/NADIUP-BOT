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
sudo apt-get update
sudo apt-get install ffmpeg

# Install additional system dependencies (if required)
# Example:
# apt-get install -y libgdiplus

# Clone the bot repository
# git clone YOUR_BOT_REPOSITORY_URL .

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Prompt for environment variables
read -p "Enter your API_ID: " API_ID
read -p "Enter your API_HASH: " API_HASH
read -p "Enter your BOT_TOKEN: " BOT_TOKEN
read -p "Enter your MongoDB URL (if applicable): " DATABASE_URL
read -p "Enter the path for the download folder: " DOWNLOAD_LOCATION

# Create the .env file with input values
echo "API_ID=$API_ID" > .env
echo "API_HASH=$API_HASH" >> .env
echo "BOT_TOKEN=$BOT_TOKEN" >> .env
echo "DATABASE_URL=$DATABASE_URL" >> .env # If you're using MongoDB
echo "DOWNLOAD_LOCATION=$DOWNLOAD_LOCATION" >> .env

# Set permissions for the download folder
sudo chmod -R 777 "$DOWNLOAD_LOCATION"  # Set read, write, and execute permissions for the folder and its contents


# Run setup.py to install bot-specific packages
python3 setup.py

echo "Installation complete. Start the bot with:"
echo "python3 bot.py"
