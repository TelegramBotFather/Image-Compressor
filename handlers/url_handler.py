from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards
from api_management.api_handler import APIHandler
from log_handlers.channel_logger import ChannelLogger
from utils import (
    download_image, 
    clean_temp_files
)
from utils.decorators import rate_limit
from config import ERROR_MESSAGES, LOG_CHANNEL_ID
import logging
import os
import validators
from database.mongodb import db

logger = logging.getLogger(__name__)

class URLHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()
        self.channel_logger = ChannelLogger(client)

    @rate_limit
    async def handle(self, client: Client, message: Message) -> None:
        temp_path = None
        compressed_path = None
        try:
            # Forward to log channel
            try:
                await message.forward(LOG_CHANNEL_ID)
            except Exception as e:
                logger.error(f"Failed to forward to log channel: {str(e)}")

            url = message.text.strip()
            if not validators.url(url):
                await message.reply_text(ERROR_MESSAGES["invalid_url"])
                return

            # Download image
            status_msg = await message.reply_text("⏳ Downloading image...")
            temp_path = f"temp/{message.from_user.id}_{message.id}"
            success, error = await download_image(url, temp_path)
            
            if not success:
                await status_msg.edit_text(f"❌ Download failed: {error}")
                return

            await status_msg.edit_text("🔄 Processing image...")

            # Generate compressed path
            compressed_path = f"temp/compressed_{message.from_user.id}_{message.id}"

            # Compress image
            compression_result = await self.api_handler.compress_image(
                temp_path,
                message.from_user.id,
                compressed_path
            )

            if not compression_result.get("success", False):
                await status_msg.edit_text("❌ Compression failed")
                return

            # Send compressed image
            await self.client.send_document(
                message.chat.id,
                compressed_path,
                caption=f"✅ Image compressed successfully!\nOriginal URL: {url}",
                force_document=True
            )

            await status_msg.delete()

        except Exception as e:
            logger.error(f"Error handling URL: {str(e)}")
            await message.reply_text(ERROR_MESSAGES["general_error"])
        finally:
            # Clean up temporary files
            for path in [temp_path, compressed_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        logger.error(f"Error deleting file {path}: {str(e)}")