from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .mongodb import db
import logging

logger = logging.getLogger(__name__)

async def get_user_api_stats(user_id: int) -> Dict[str, Any]:
    """Get user's API usage statistics."""
    try:
        today = datetime.utcnow().date()
        
        # Get today's stats
        today_stats = await db.api_stats.find_one({
            "user_id": user_id,
            "date": today.isoformat()
        }) or {"files": 0, "size": 0}
        
        # Get total stats
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_files": {"$sum": "$files"},
                "total_size": {"$sum": "$size"}
            }}
        ]
        total_stats = await db.api_stats.aggregate(pipeline).to_list(1)
        total_stats = total_stats[0] if total_stats else {"total_files": 0, "total_size": 0}
        
        return {
            "today_files": today_stats["files"],
            "today_size": today_stats["size"],
            "total_files": total_stats["total_files"],
            "total_size": total_stats["total_size"]
        }
        
    except Exception as e:
        logger.error(f"Error getting API stats for user {user_id}: {str(e)}")
        return {
            "today_files": 0,
            "today_size": 0,
            "total_files": 0,
            "total_size": 0
        }

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
        # Add timestamp if not present
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.now()
            
        await db.api_logs.insert_one(log_data)
        
        # Update user's total stats
        await db.api_stats.update_one(
            {"user_id": log_data["user_id"]},
            {
                "$inc": {
                    "total_calls": 1,
                    "total_size": log_data.get("size", 0)
                },
                "$set": {
                    "last_used": log_data["timestamp"]
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error saving API log: {str(e)}")
        return False

async def remove_api_key(user_id: int) -> bool:
    """
    Remove user's API key.
    
    Args:
        user_id (int): The Telegram user ID
        
    Returns:
        bool: True if key was removed, False otherwise
    """
    try:
        result = await db.api_keys.delete_one({"user_id": user_id})
        return bool(result.deleted_count)
    except Exception as e:
        logger.error(f"Error removing API key: {str(e)}")
        return False