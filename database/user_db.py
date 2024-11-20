from typing import Optional, Dict, Any
from datetime import datetime
from .mongodb import db
import logging

logger = logging.getLogger(__name__)

async def save_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None
) -> bool:
    """
    Save or update user information in the database.

    Args:
        user_id (int): The Telegram user ID.
        username (Optional[str]): The Telegram username.
        first_name (Optional[str]): The user's first name.

    Returns:
        bool: True if operation is successful, False otherwise.
    """
    try:
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "username": username,
                    "first_name": first_name,
                    "last_active": datetime.utcnow()
                },
                "$setOnInsert": {
                    "joined_date": datetime.utcnow(),
                    "banned": False,
                    "total_compressions": 0,
                    "total_size_saved": 0
                }
            },
            upsert=True
        )
        logger.info(f"User {user_id} saved/updated successfully.")
        return True
    except Exception as e:
        logger.error(f"Error saving user {user_id}: {str(e)}")
        return False

async def get_user_settings(user_id: int) -> Dict[str, Any]:
    """
    Retrieve user settings from the database.

    Args:
        user_id (int): The Telegram user ID.

    Returns:
        Dict[str, Any]: A dictionary of user settings.
    """
    try:
        settings = await db.settings.find_one({"user_id": user_id})
        if not settings:
            settings = {
                "user_id": user_id,
                "default_format": "jpeg",
                "notifications_enabled": True,
                "custom_api_key": None,
                "created_at": datetime.utcnow()
            }
            await db.settings.insert_one(settings)
            logger.info(f"Default settings created for user {user_id}.")
        return settings
    except Exception as e:
        logger.error(f"Error retrieving settings for user {user_id}: {str(e)}")
        return {}

async def save_user_log(log_data: Dict[str, Any]) -> bool:
    """
    Save a log entry for user actions.

    Args:
        log_data (Dict[str, Any]): The log data to save.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        await db.user_logs.insert_one(log_data)
        logger.info(f"User action log saved for user {log_data.get('user_id')}.")
        return True
    except Exception as e:
        logger.error(f"Error saving user log: {str(e)}")
        return False

async def update_user_stats(
    user_id: int,
    original_size: int,
    compressed_size: int
) -> None:
    """
    Update user compression statistics.

    Args:
        user_id (int): The Telegram user ID.
        original_size (int): The original size of the image.
        compressed_size (int): The compressed size of the image.
    """
    try:
        size_saved = original_size - compressed_size
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "total_compressions": 1,
                    "total_size_saved": size_saved
                },
                "$set": {"last_active": datetime.utcnow()}
            }
        )
        
        # Update daily stats
        today = datetime.utcnow().date()
        await db.usage_stats.update_one(
            {
                "user_id": user_id,
                "date": today
            },
            {
                "$inc": {
                    "compressions": 1,
                    "size_saved": size_saved
                }
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating stats for user {user_id}: {str(e)}")

async def update_user_settings(user_id: int, settings_update: Dict[str, Any]) -> bool:
    """
    Update user settings in the database.

    Args:
        user_id (int): The Telegram user ID
        settings_update (Dict[str, Any]): Dictionary containing settings to update

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = await db.settings.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    **settings_update,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        logger.info(f"Settings updated for user {user_id}")
        return bool(result.modified_count or result.upserted_id)
    except Exception as e:
        logger.error(f"Error updating settings for user {user_id}: {str(e)}")
        return False