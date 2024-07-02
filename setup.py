from setuptools import setup, find_packages
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install dependencies
install_requirements = ["aiohttp", "beautifulsoup4", "hachoir", "numpy", "Pillow", "pyrogram", 
                       "requests", "tgcrypto", "yt-dlp", "olefile", "motor", "pymongo", "dnspython", 
                       "ffmpeg-python", "ffmpeg", "psutil", "loggers", "filetype", "tldextract",
                       "aiofiles", "pyromod", "flask", "gunicorn==22.0.0", "libtorrent==2.0.9", "unrar"]

setup(
    name='nadiup-bot',
    version='1.0.0',
    description='NadiuP Bot - Telegram URL Uploader',
    packages=find_packages(),
    install_requires=install_requirements,
)

# Run the bot (optional, you might want to start it manually)
# subprocess.check_call(["python3", "bot.py"]) 
