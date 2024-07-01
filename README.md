
```markdown
# NadiuP Bot - Telegram URL Uploader

**A powerful Telegram bot for downloading and uploading files from URLs, managing torrents, and extracting archives.**

## Features

* **Download from URLs:** Supports a wide range of websites and file types, including videos, audio, documents, and archives.
* **Direct Link Generation:** Create shareable direct download links for your Telegram files using file.io.
* **Torrent Support:** Download torrents directly to your Telegram chats.
* **Custom Thumbnails:** Set custom thumbnails for your videos and files.
* **File Conversion:** Convert videos to audio (MP3) and change document formats (details coming soon!).
* **Archive Extraction:** Easily unzip or extract files from supported archive formats (zip, rar).
* **Audio Extraction:** Extract audio tracks from videos.
* **User-Friendly Interface:** Interactive menus and helpful messages guide you through the process.
* **Enhanced Progress Bars:**  Track download and upload progress with detailed information, including speed and ETA.

## Getting Started

### 1. Server Setup

* **Operating System:**  Linux (Ubuntu, Debian, CentOS, etc.) is recommended.
* **Python:** Python 3.9 or higher.
* **Pip:**  Python's package installer (`pip`).
* **MongoDB (Optional):**  If you're using a MongoDB database for your bot. 
* **Storage:** At least 10GB of free disk space is recommended for storing downloaded files.

### 2. Installation

1. **Create a virtual environment:**

   ```bash
   python3 -m venv .venv 
   ```

2. **Activate the virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install `unrar` (for RAR extraction):**

   ```bash
   sudo apt-get update 
   sudo apt-get install unrar 
   ```

### 3. Configure Environment Variables

1. **Create a `.env` file:**
   * In the root directory of your project, create a file named `.env`.
   * Add the following lines (replacing with your actual values):

   ```
   API_ID=YOUR_API_ID
   API_HASH=YOUR_API_HASH
   BOT_TOKEN=YOUR_BOT_TOKEN
   DATABASE_URL=YOUR_MONGODB_URL # (if you are using MongoDB)
   ```

2. **Load Environment Variables:**
   - Update your `config.py` file to load environment variables:

     ```python
     import os
     from dotenv import load_dotenv
     load_dotenv()  # Load the environment variables from the .env file

     API_ID = os.getenv("API_ID")
     API_HASH = os.getenv("API_HASH")
     BOT_TOKEN = os.getenv("BOT_TOKEN")
     DATABASE_URL = os.getenv("DATABASE_URL")  # (if you are using MongoDB)
     # ... add other config variables as needed
     ```

   - Install the `dotenv` package:

     ```bash
     pip install python-dotenv
     ```

### 4. Run the Bot

1. **Run `setup.py` to install dependencies and start the bot:**

   ```bash
   python3 setup.py
   ```

2. **Manually start the bot:**

   ```bash
   python3 bot.py
   ```

## Usage

1. **Start a chat with the bot:** Search for `@nadiupbot` on Telegram and start a conversation.
2. **Send a URL:** Send the bot a direct link to the file you want to download.
3. **Select Format (if applicable):** The bot will present you with options to choose the desired file format and size.
4. **Wait for the download and upload:** The bot will download the file and then upload it to Telegram. 

**Commands:**

* `/start`: Start the bot.
* `/help`: View available commands and features.
* `/about`:  Learn more about the bot.
* `/settings`: Configure your preferences. 
* `/delthumb`: Delete your custom thumbnail.
* `/showthumb`: View your current custom thumbnail.
* `/extractaudio`: Extract audio from a video (reply to the video with this command).
* `/unzip`: Extract files from a zip or rar archive (reply to the archive file with this command). 
* `/torrent`:  Download a torrent (reply to a torrent file or magnet link with this command).
* `/directlink`:  Generate a direct download link (reply to a document with this command).

## Support

If you encounter any issues or need help, please contact the developer at [@yahyatoubali](https://t.me/yahyatoubali).

## Contributing

Contributions are welcome! If you'd like to add new features or improve the bot, please fork the repository and submit a pull request.

## License

[MIT License](LICENSE)
```

**Key Improvements:**

*   **More Specific Features:**  Clarified the bot's functionality with a detailed list of features.
*   **Better Organization:**  Improved the structure of the README with a clear hierarchy of sections for easier readability.
*   **Updated Installation Instructions:**  Provided step-by-step instructions on how to set up a virtual environment, install dependencies, and configure the bot on a server.
*   **Clear Environment Variable Guide:**  Added detailed instructions on how to set environment variables using a `.env` file. 
*   **Removed Redundant Information:** Streamlined the README by removing unnecessary notes.

This is a more complete and user-friendly README that will help people understand and use your bot! Feel free to ask any further questions. 
