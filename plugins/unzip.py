#  @yahyatoubali

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
import zipfile
import shutil
from time import sleep
from plugins.script import Translation
from plugins.config import Config
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
import subprocess

@Client.on_message(filters.command("unzip") & filters.private)
async def unzip_files(bot:Client, message: Message):
    if message.reply_to_message:
        try:
            # Check if the replied message is a document
            if message.reply_to_message.document:
                await message.reply_chat_action(enums.ChatAction.TYPING)
                # Download the document
                download_location = await bot.download_media(
                    message=message.reply_to_message.document,
                    file_name=Config.DOWNLOAD_LOCATION + "/",
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.DOWNLOAD_START,
                        message,
                        time.time()
                    )
                )
                if download_location is None:
                    return await message.edit_text(Translation.DOWNLOAD_FAILED)

                # Call the Bash script for extraction
                extract_dir = os.path.dirname(download_location)
                subprocess.run(["bash", "extract_archive.sh", download_location, extract_dir])

                # Upload extracted files
                for filename in os.listdir(extract_dir):
                    filepath = os.path.join(extract_dir, filename)
                    try:
                        await bot.send_document(
                            chat_id=message.chat.id,
                            document=filepath,
                            caption=f"Extracted: `{filename}`",
                            disable_notification=True
                        )
                    except Exception as e:
                        await message.reply_text(f"**Error uploading extracted file {filename}:** {e}")

                # Clean up extracted files
                shutil.rmtree(extract_dir)
                os.remove(download_location)
                return
            else:
                await message.edit_text("**Please reply to a document to unzip it.**")
        except Exception as e:
            await message.edit_text(f"**Error:** {e}")
            logger.error(f"Error in unzip_files: {e}")
    else:
        await message.reply_text("**Please reply to a document to unzip it.**")
