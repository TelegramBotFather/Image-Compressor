from pyrogram import Client
from pyrogram.types import Message
from api_management.api_handler import APIHandler
from utils.helpers import get_image_info, format_size
from config import MAX_FILE_SIZE, ERROR_MESSAGES, LOG_CHANNEL_ID
from database.mongodb import db
import os
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()

    async def handle(self, client: Client, message: Message) -> None:
        temp_path = None
        compressed_path = None
        progress_message = None
        
        try:
            user_id = message.from_user.id
            
            # Get file info based on message type
            if message.photo:
                file_id = message.photo.file_id
                file_name = f"{file_id}"
            elif message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
            else:
                await message.reply_text(ERROR_MESSAGES["invalid_format"])
                return

            # Get user's format preference
            user_settings = await db.settings.find_one({"user_id": user_id})
            target_format = user_settings.get("current_format", "jpeg")

            # Set proper file extension based on target format
            temp_path = f"temp/temp_{file_id}.{target_format}"
            compressed_path = f"temp/compressed_{file_id}.{target_format}"

            # Download file
            progress_message = await message.reply_text("⏳ Downloading file...")
            await message.download(temp_path)

            if progress_message:
                await progress_message.edit_text("🔄 Processing image...")

            # Compress image
            compression_result = await self.api_handler.compress_image(
                input_path=temp_path,
                user_id=user_id,
                output_path=compressed_path,
                target_format=target_format
            )

            if not compression_result.get("success", False):
                if progress_message:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Send as document to preserve format
            await message.reply_document(
                document=compressed_path,
                caption=f"✅ Image compressed and converted to {target_format.upper()}",
                force_document=True
            )

            if progress_message:
                await progress_message.delete()

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            if progress_message:
                await progress_message.edit_text(ERROR_MESSAGES["general_error"])
