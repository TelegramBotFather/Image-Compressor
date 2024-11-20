from typing import Optional, Tuple
import tinify
from log_handlers.api_logger import APILogger
from datetime import datetime
from database.user_db import update_user_stats
from config import TINIFY_API_KEY
from database.mongodb import db
import os
from pyrogram.types import Message
from components.keyboards import Keyboards
import logging

logger = logging.getLogger(__name__)

class APIHandler:
    """Handler for interacting with the TinyPNG API."""

    def __init__(self):
        self.api_logger = APILogger()
        self.default_api_key = os.getenv("TINIFY_API_KEY")

    async def get_api_key(self, user_id: int) -> str:
        """
        Retrieve the user's API key or return the default key if none is set.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            str: The API key to be used.
        """
        try:
            if user_id in self._api_cache:
                return self._api_cache[user_id]
            
            user_key = await self._get_user_api_key(user_id)
            if user_key:
                self._api_cache[user_id] = user_key
                return user_key
            
            return self.default_api_key
        except Exception as e:
            logger.error(f"Error getting API key: {str(e)}")
            return self.default_api_key

    async def compress_image(
        self,
        file_path: str,
        user_id: int,
        target_format: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Compress an image using the TinyPNG API.

        Args:
            file_path (str): Path to the original image.
            user_id (int): The Telegram user ID.

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: Compression result, path to the compressed image, and error message if any.

        Raises:
            Exception: If compression fails.
        """
        try:
            # Create temp directory if it doesn't exist
            os.makedirs("temp", exist_ok=True)
            
            api_key = await self.get_api_key(user_id)
            tinify.key = api_key
            
            source = tinify.from_file(file_path)
            
            if target_format:
                source = source.convert(format=target_format)
            
            compressed_filename = f"compressed_{datetime.now().timestamp()}.{target_format or 'png'}"
            compressed_path = os.path.join("temp", compressed_filename)
            
            source.to_file(compressed_path)
            
            # Update statistics
            original_size = os.path.getsize(file_path)
            compressed_size = os.path.getsize(compressed_path)
            await update_user_stats(user_id, original_size, compressed_size)
            
            # Log successful API call
            await self.api_logger.log_api_call(
                user_id=user_id,
                api_key=api_key,
                success=True,
                response={"compressed_path": compressed_path}
            )
            
            return True, compressed_path, None
            
        except tinify.AccountError as e:
            logger.error(f"Account error: {str(e)}")
            return False, None, "API key error. Please try again later."
        except tinify.ClientError as e:
            logger.error(f"Client error: {str(e)}")
            return False, None, "Invalid image or format."
        except tinify.ServerError as e:
            logger.error(f"Server error: {str(e)}")
            return False, None, "Service temporarily unavailable."
        except Exception as e:
            logger.error(f"Compression error: {str(e)}")
            return False, None, "Failed to compress image. Please try again."

    async def _get_user_api_key(self, user_id: int) -> Optional[str]:
        """
        Retrieve user's custom API key from database.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            Optional[str]: The user's custom API key.
        """
        try:
            result = await db.api_keys.find_one({"user_id": user_id})
            return result["api_key"] if result else None
        except Exception as e:
            logger.error(f"Error retrieving API key: {str(e)}")
            return None