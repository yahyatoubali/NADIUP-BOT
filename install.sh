#!/bin/bash

# Check if root user
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

# Detect operating system
OS=$(uname -s)

# Function to install packages for Ubuntu/Debian
install_ubuntu() {
  apt-get update -y
  apt-get install -y python3 python3-pip python3-venv git unrar ffmpeg 
}

# Function to install packages for CentOS
install_centos() {
  yum update -y
  yum install -y python3 python3-pip python3-venv git unrar ffmpeg 
}

# Function to install packages for Arch Linux
install_arch() {
  pacman -Syu
  pacman -S python python-pip python-virtualenv git unrar ffmpeg
}

# Install packages based on OS
if [ "$OS" == "Linux" ]; then
  if [ -f /etc/redhat-release ]; then
    install_centos
  elif [ -f /etc/debian_version ]; then
    install_ubuntu
  elif [ -f /etc/arch-release ]; then
    install_arch
  else
    echo "Unsupported operating system."
    exit 1
  fi
fi


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
sudo chmod -R 777 "$DOWNLOAD_LOCATION"  # Set permissions

# Run setup.py to install bot-specific packages
python3 setup.py

echo "Installation complete. Start the bot with:"
echo "python3 bot.py"
