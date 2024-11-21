from typing import Optional
from pyrogram import Client
from datetime import datetime
import logging
from config import LOG_CHANNEL_ID
from components.keyboards import Keyboards
from pyrogram.enums import ParseMode

logger = logging.getLogger(__name__)

class ChannelLogger:
    def __init__(self, client: Client):
        self.client = client
        self.log_channel = LOG_CHANNEL_ID

    async def log_new_user(self, user_id: int, username: str = None) -> None:
        """Log new user registration."""
        try:
            text = (
                "👤 New User\n"
                f"ID: `{user_id}`\n"
                f"Username: {'@' + username if username else 'None'}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.client.send_message(self.log_channel, text)
        except Exception as e:
            logger.error(f"Error logging new user: {str(e)}")

    async def log_image_process(
        self,
        user_id: int,
        original_size: int,
        compressed_size: int
    ) -> None:
        """Log image processing."""
        try:
            saved = original_size - compressed_size
            saved_percent = (saved / original_size) * 100 if original_size > 0 else 0
            
            text = (
                "🖼 Image Processed\n"
                f"User ID: `{user_id}`\n"
                f"Original Size: {original_size/1024:.1f}KB\n"
                f"Compressed Size: {compressed_size/1024:.1f}KB\n"
                f"Saved: {saved/1024:.1f}KB ({saved_percent:.1f}%)\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.client.send_message(self.log_channel, text)
        except Exception as e:
            logger.error(f"Error logging image process: {str(e)}")

    async def log_error(self, error_message: str, user_id: int = None) -> None:
        """Log errors."""
        try:
            text = (
                "❌ Error Occurred\n"
                f"User ID: `{user_id if user_id else 'N/A'}`\n"
                f"Error: {error_message}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.client.send_message(self.log_channel, text)
        except Exception as e:
            logger.error(f"Error logging error message: {str(e)}")

    async def log_image_request(self, user_id: int, username: str, message_type: str) -> None:
        """Log image compression requests."""
        try:
            text = (
                "📥 New Image Request\n"
                f"User ID: `{user_id}`\n"
                f"Username: @{username}\n"
                f"Type: {message_type}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await self.client.send_message(
                self.log_channel,
                text,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error logging image request: {str(e)}")