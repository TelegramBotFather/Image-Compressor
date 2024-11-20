from typing import Optional, Dict, Any
from datetime import datetime
from .mongodb import db
import logging

logger = logging.getLogger(__name__)

async def save_api_key(user_id: int, api_key: str) -> bool:
    """Save user's API key."""
    try:
        await db.api_keys.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "api_key": api_key,
                    "updated_at": datetime.now()
                },
                "$setOnInsert": {
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error saving API key: {str(e)}")
        return False

async def get_user_api_key(user_id: int) -> Optional[str]:
    """Get user's API key."""
    try:
        doc = await db.api_keys.find_one({"user_id": user_id})
        return doc["api_key"] if doc else None
    except Exception as e:
        logger.error(f"Error getting API key: {str(e)}")
        return None

async def save_api_log(log_data: Dict[str, Any]) -> bool:
    """Save API call log."""
    try:
        await db.logs.insert_one(log_data)
        return True
    except Exception as e:
        logger.error(f"Error saving API log: {str(e)}")
        return False