#  @yahyatoubali

import asyncio
import os
import requests
import aiofiles
import tempfile

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from plugins.config import Config
from plugins.script import Translation

# --- Function to upload to file.io (for now, it's the only provider) ---
async def upload_to_fileio(file_path):
    """Uploads a file to file.io and returns the download link."""
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        response = requests.post("https://file.io", files=files) 

    if response.status_code == 200:
        data = response.json()
        return data['link']  # The direct download link
    else:
        raise Exception(f"Error uploading file to file.io: {response.text}")

@Client.on_message(filters.command("directlink") & filters.private)
async def generate_direct_link(bot: Client, message: Message):
    if message.reply_to_message:
        # ... (Existing logic for handling replied messages) ... 

    elif message.document: 
        # Handle uploaded documents 
        file_name = message.document.file_name.lower()
        if file_name.endswith(".sh"):
            await message.reply_text("Sorry, I cannot process .sh files. Please try a different file type.")
            return
        else:
            await process_file(bot, message)

    elif message.forward_from:
        # Handle forwarded files
        if message.forward_from.is_bot:
            return  # Ignore forwarded files from bots
        if message.forward_from.id == Config.OWNER_ID:
            return  # Ignore forwarded files from the bot's owner
        await process_file(bot, message)

    else:
        await message.reply_text("Please reply to a document or forward a file.")


async def process_file(bot: Client, message: Message):
    """Handles uploaded or forwarded files."""
    try:
        await message.reply_chat_action(enums.ChatAction.TYPING)

        # Use tempfile.NamedTemporaryFile to create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Download the file to the temporary file
            download_location = await bot.download_media(
                message=message.document or message.video or message.audio or message.photo,
                file_name=temp_file.name
            )

            if download_location is None:
                return await message.edit_text(Translation.DOWNLOAD_FAILED)

            # Upload to file.io
            direct_link = await upload_to_fileio(temp_file.name)

            if direct_link:
                await message.reply_text(
                    f"**Direct Link:** `{direct_link}`\n\n**Note:** This link will expire in 14 days."
                )

    except Exception as e:
        await message.reply_text(f"Error: {e}")
