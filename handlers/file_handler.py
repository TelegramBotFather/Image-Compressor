from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from utils.helpers import get_image_info, clean_temp_files, format_size
from api_management.api_handler import APIHandler
from components.messages import Messages
from components.keyboards import Keyboards
from config import MAX_FILE_SIZE, SUPPORTED_FORMATS, ERROR_MESSAGES, LOG_CHANNEL_ID
import os
import logging
import time
from database.user_db import get_user_settings
from log_handlers.channel_logger import ChannelLogger
from utils.error_handler import handle_error

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
                file_id = message.photo.file_id
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
            await handle_error(message, e)
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
                output_format
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

            # Send compressed image to user
            sent_message = await original_message.reply_document(
                document=compressed_path,
                caption=caption,
                force_document=True
            )

            # Forward to log channel
            await self.client.send_document(
                LOG_CHANNEL_ID,
                compressed_path,
                caption=(
                    f"👤 User: {original_message.from_user.mention}\n"
                    f"🆔 User ID: `{original_message.from_user.id}`\n"
                    f"📊 Original Size: {format_size(original_size)}\n"
                    f"📊 Compressed Size: {format_size(compressed_size)}\n"
                    f"💹 Space Saved: {saved_percentage:.1f}%"
                )
            )

            await progress_message.delete()

        except Exception as e:
            logger.error(f"Error sending compressed image: {str(e)}")
            await progress_message.edit_text(ERROR_MESSAGES["general_error"])

    async def handle_image(self, message: Message) -> None:
        """Handle image file uploads."""
        temp_path = None
        compressed_path = None
        
        try:
            # Download file
            progress_msg = await message.reply_text("⏳ Downloading image...")
            
            # Create temp paths
            temp_path = f"temp/temp_{message.document.file_id}.jpg"
            compressed_path = f"temp/compressed_{message.document.file_id}.jpg"
            
            # Download the file
            await message.download(
                file_name=temp_path
            )
            
            # Verify file size
            if os.path.getsize(temp_path) > MAX_FILE_SIZE:
                await progress_msg.edit_text(ERROR_MESSAGES["file_too_large"])
                return

            # Check if it's a valid image
            is_valid, info = await get_image_info(temp_path)
            if not is_valid:
                await progress_msg.edit_text(ERROR_MESSAGES["invalid_image"])
                return

            await progress_msg.edit_text("🔄 Processing image...")

            # Compress image
            compression_result = await self.api_handler.compress_image(
                input_path=temp_path,
                user_id=message.from_user.id,
                output_path=compressed_path
            )

            if not compression_result.get("success", False):
                logger.error(f"Compression failed: {compression_result.get('error', 'Unknown error')}")
                await progress_msg.edit_text(ERROR_MESSAGES["general_error"])
                return

            # Calculate stats
            original_size = os.path.getsize(temp_path)
            compressed_size = os.path.getsize(compressed_path)
            saved_percentage = ((original_size - compressed_size) / original_size) * 100

            # Send to user
            caption = (
                "✅ Image compressed successfully!\n\n"
                f"Original Size: {format_size(original_size)}\n"
                f"Compressed Size: {format_size(compressed_size)}\n"
                f"Space Saved: {saved_percentage:.1f}%"
            )

            await message.reply_document(
                document=compressed_path,
                caption=caption,
                force_document=True
            )

            # Send to log channel
            await self.client.send_document(
                LOG_CHANNEL_ID,
                compressed_path,
                caption=(
                    f"👤 User: {message.from_user.mention}\n"
                    f"🆔 User ID: `{message.from_user.id}`\n"
                    f"📊 Original Size: {format_size(original_size)}\n"
                    f"📊 Compressed Size: {format_size(compressed_size)}\n"
                    f"💹 Space Saved: {saved_percentage:.1f}%"
                )
            )

            await progress_msg.delete()

            # Update user stats
            await update_user_stats(
                message.from_user.id,
                original_size,
                compressed_size
            )

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            if progress_msg:
                await progress_msg.edit_text(ERROR_MESSAGES["general_error"])
        finally:
            # Cleanup temporary files
            for path in [temp_path, compressed_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        logger.info(f"Deleted temporary file: {path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {path}: {str(e)}")
