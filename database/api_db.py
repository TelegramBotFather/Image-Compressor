from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .mongodb import db
import logging

logger = logging.getLogger(__name__)

async def get_user_api_stats(user_id: int) -> Dict[str, Any]:
    """Get user's API usage statistics."""
    try:
        # Get today's date at midnight for accurate daily stats
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query for user's stats
        stats = await db.api_stats.find_one({"user_id": user_id})
        
        if not stats:
            return {
                "total_calls": 0,
                "total_size": 0,
                "today_calls": 0,
                "today_size": 0,
                "last_used": datetime.now()
            }
            
        # Calculate today's usage
        today_stats = await db.api_logs.aggregate([
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": today}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "calls": {"$sum": 1},
                    "size": {"$sum": "$size"}
                }
            }
        ]).to_list(1)

        today_calls = today_stats[0]["calls"] if today_stats else 0
        today_size = today_stats[0]["size"] if today_stats else 0

        return {
            "total_calls": stats.get("total_calls", 0),
            "total_size": stats.get("total_size", 0),
            "today_calls": today_calls,
            "today_size": today_size,
            "last_used": stats.get("last_used", datetime.now())
        }
        
    except Exception as e:
        logger.error(f"Error getting API stats for user {user_id}: {str(e)}")
        return {
            "total_calls": 0,
            "total_size": 0,
            "today_calls": 0,
            "today_size": 0,
            "last_used": datetime.now()
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