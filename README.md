# NadiuP Bot - Telegram URL Uploader

**A powerful Telegram bot for downloading and uploading files from URLs.**

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy) 

## Features

* **Download from URLs:** Supports a wide range of websites and file types, including videos, audio, documents, and archives.
* **Direct Link Generation:** Generate direct download links for your Telegram files using file.io.
* **Torrent Support:** Download torrents directly from magnet links or torrent files.
* **Custom Thumbnails:** Set custom thumbnails for your videos and files.
* **File Conversion:**  Convert videos to audio (MP3) and change document formats (details coming soon!).
* **Archive Extraction:** Easily unzip or extract files from supported archive formats.
* **Audio Extraction:** Extract audio tracks from videos.
* **User-Friendly Interface:** Interactive menus and helpful messages guide you through the process.
* **Enhanced Progress Bars:**  Track download and upload progress with detailed information.

## Getting Started

### 1. Deploy to Heroku

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy) 

Click the button above to deploy NadiuP Bot to Heroku. 

### 2. Configure Environment Variables

After deploying to Heroku, you'll need to set the following environment variables:

* `BOT_TOKEN`: Your bot token from BotFather.
* `API_ID`: Your Telegram API ID.
* `API_HASH`: Your Telegram API hash.
* `DATABASE_URL`: Your MongoDB database URL.
* `LOG_CHANNEL`: Your Telegram channel ID for logging (optional).
* `UPDATES_CHANNEL`: Your Telegram channel ID for force subscribe (optional).
* `OWNER_ID`: Your Telegram user ID.

### 3. Start the Bot

Once you have configured the environment variables, start the bot on Heroku. It will be ready to use!

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

If you encounter any issues or need help, please contact the developer at [@yahyatoubali](https://t.me/yahyatoubali) or join the [NT Bots Support](https://t.me/NT_BOTS_SUPPORT) group.

## Contributing

Contributions are welcome! If you'd like to add new features or improve the bot, please fork the repository and submit a pull request.

## License

[MIT License](LICENSE)
