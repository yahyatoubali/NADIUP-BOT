#  @yahyatoubali

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
import zipfile
import patool
import shutil
from time import sleep
from plugins.script import Translation
from plugins.config import Config
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)

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

                # Check if the downloaded file is a zip archive
                if zipfile.is_zipfile(download_location):
                    # Extract the zip archive
                    with zipfile.ZipFile(download_location, 'r') as zip_ref:
                        zip_ref.extractall(os.path.dirname(download_location))
                    await message.edit_text(f"**Successfully extracted all files!**")
                    os.remove(download_location)
                    return

                elif patool.util.get_archive_format(download_location):  # Use patool here
                    # Extract the archive using patool
                    extract_location = os.path.splitext(download_location)[0]
                    try:
                        patool.extract_archive(download_location, outdir=extract_location) # Use patool here
                    except Exception as e:
                        return await message.edit_text(f"**Error extracting archive:** {e}")

                    await message.edit_text(f"**Successfully extracted all files!**")
                    os.remove(download_location)

                    # Upload extracted files
                    for filename in os.listdir(extract_location):
                        filepath = os.path.join(extract_location, filename)
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
                    shutil.rmtree(extract_location)
                    return

                else:
                    await message.edit_text(
                        "**This file is not a supported archive format (zip, rar)!**"
                    )
                    os.remove(download_location)
                    return
            else:
                await message.edit_text("**Please reply to a document to unzip it.**")
        except Exception as e:
            await message.edit_text(f"**Error:** {e}")
            logger.error(f"Error in unzip_files: {e}")
    else:
        await message.reply_text("**Please reply to a document to unzip it.**")
