from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from utils.helpers import get_image_info, clean_temp_files, format_size
from api_management.api_handler import APIHandler
from components.messages import Messages
from components.keyboards import Keyboards
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS, ERROR_MESSAGES
import os
import logging
import time
from database.user_db import get_user_settings
from log_handlers.channel_logger import ChannelLogger

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self, client: Client):
        self.client = client
        self.api_handler = APIHandler()
        self.channel_logger = ChannelLogger(client)

    async def handle(self, client: Client, message: Message) -> None:
        """Handle incoming photo or document messages."""
        try:
            user_id = message.from_user.id
            username = message.from_user.username or "No username"
            
            # Log to channel
            await self.channel_logger.log_image_request(
                user_id=user_id,
                username=username,
                message_type="photo" if message.photo else "document"
            )
            
            # Get file info based on message type
            if message.photo:
                # Updated photo handling
                file_id = message.photo[-1].file_id
                file_name = f"{file_id}.jpg"
                mime_type = "image/jpeg"
            elif message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
                mime_type = message.document.mime_type
            else:
                await message.reply_text(ERROR_MESSAGES["invalid_format"])
                return

            # Validate file format
            if not any(ext in file_name.lower() for ext in SUPPORTED_FORMATS):
                await message.reply_text(ERROR_MESSAGES["invalid_format"])
                return

            # Download file
            progress_message = await message.reply_text("⏳ Downloading file...")
            temp_path = os.path.join("temp", f"temp_{file_id}_{file_name}")
            
            try:
                await message.download(temp_path)
            except Exception as e:
                logger.error(f"Error downloading file: {str(e)}")
                await progress_message.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Process the image
            await self._process_image(message, progress_message, temp_path, file_name)

        except Exception as e:
            logger.error(f"Error handling file: {str(e)}")
            await message.reply_text(ERROR_MESSAGES["general_error"])
        finally:
            # Cleanup
            if 'temp_path' in locals():
                await clean_temp_files([temp_path])

    async def _process_image(self, message: Message, progress_message: Message, temp_path: str, file_name: str) -> None:
        """Process the downloaded image."""
        try:
            # Get user settings
            user_settings = await get_user_settings(message.from_user.id)
            output_format = user_settings.get('default_format', 'jpeg')

            # Update progress
            await progress_message.edit_text("🔄 Processing image...")

            # Compress image
            compressed_path = os.path.join("temp", f"compressed_{file_name}")
            compression_result = await self.api_handler.compress_image(
                temp_path, 
                compressed_path,
                output_format,
                message.from_user.id
            )

            if compression_result.get("success"):
                # Send compressed image
                await self._send_compressed_image(
                    message,
                    progress_message,
                    compressed_path,
                    compression_result
                )
            else:
                await progress_message.edit_text(ERROR_MESSAGES["general_error"])

        except Exception as e:
            await handle_error(message, e, "Error processing image")
            await progress_message.edit_text(ERROR_MESSAGES["general_error"])
        finally:
            # Cleanup
            if 'compressed_path' in locals():
                await clean_temp_files([compressed_path])

    async def _send_compressed_image(
        self,
        original_message: Message,
        progress_message: Message,
        compressed_path: str,
        compression_result: dict
    ) -> None:
        """Send the compressed image with stats."""
        try:
            # Calculate compression stats
            original_size = os.path.getsize(compressed_path)
            compressed_size = compression_result.get("compressed_size", 0)
            saved_percentage = ((original_size - compressed_size) / original_size) * 100

            # Prepare caption
            caption = (
                "✅ Image compressed successfully!\n\n"
                f"Original Size: {format_size(original_size)}\n"
                f"Compressed Size: {format_size(compressed_size)}\n"
                f"Space Saved: {saved_percentage:.1f}%"
            )

            # Send compressed image
            await original_message.reply_document(
                document=compressed_path,
                caption=caption,
                force_document=True
            )
            await progress_message.delete()

        except Exception as e:
            logger.error(f"Error sending compressed image: {str(e)}")
            await progress_message.edit_text(ERROR_MESSAGES["general_error"])