#  @yahyatoubali

import asyncio
import os
import requests
import aiofiles
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from plugins.config import Config
from plugins.script import Translation

@Client.on_message(filters.command("directlink") & filters.private)
async def generate_direct_link(bot: Client, message: Message):
    if message.reply_to_message:
        if message.reply_to_message.document:
            try:
                await message.reply_chat_action(enums.ChatAction.TYPING)
                # Download the file to a temporary location
                download_location = await bot.download_media(
                    message=message.reply_to_message.document,
                    file_name=Config.DOWNLOAD_LOCATION + "/" 
                )
                if download_location is None:
                    return await message.edit_text(Translation.DOWNLOAD_FAILED)

                # Upload to file.io
                async with aiofiles.open(download_location, 'rb') as file:
                    file_data = await file.read()
                
                response = requests.post("https://file.io", files={"file": file_data})

                if response.status_code == 200:
                    data = response.json()
                    direct_link = data['link']
                    await message.reply_text(
                        f"**Direct Link:** `{direct_link}`\n\n**Note:** This link will expire in 14 days."
                    )
                else:
                    await message.reply_text(f"Error generating direct link: {response.text}")

                # Clean up the downloaded file
                os.remove(download_location)
            except Exception as e:
                await message.reply_text(f"Error: {e}")
        else:
            await message.reply_text("Please reply to a document.")
    else:
        await message.reply_text("Please reply to a document.")
