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
            
            # Forward to log channel
            try:
                await message.forward(LOG_CHANNEL_ID)
            except Exception as e:
                logger.error(f"Failed to forward to log channel: {str(e)}")

            # Get file info based on message type
            if message.photo:
                file_id = message.photo.file_id
                file_name = f"{file_id}.jpg"
            elif message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
            else:
                await message.reply_text(ERROR_MESSAGES["invalid_format"])
                return

            # Set paths
            temp_path = f"temp/{file_name}"
            compressed_path = f"temp/compressed_{file_name}"

            # Download file
            progress_message = await message.reply_text("⏳ Downloading file...")
            await message.download(temp_path)

            if progress_message:
                await progress_message.edit_text("🔄 Processing image...")

            # Compress image
            compression_result = await self.api_handler.compress_image(
                input_path=temp_path,
                user_id=user_id,
                output_path=compressed_path
            )

            if not compression_result.get("success", False):
                if progress_message:
                    await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Send compressed image
            await message.reply_document(
                document=compressed_path,
                caption="✅ Image compressed successfully!",
                force_document=True
            )

            if progress_message:
                await progress_message.delete()

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            if progress_message:
                await progress_message.edit_text(ERROR_MESSAGES["general_error"])
