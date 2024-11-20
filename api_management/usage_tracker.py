from typing import Dict, Any
from datetime import datetime
from database.api_db import get_user_api_stats
import logging

logger = logging.getLogger(__name__)

class UsageTracker:
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user's API usage statistics."""
        try:
            stats = await get_user_api_stats(user_id)
            return {
                "total_calls": stats.get("total_calls", 0),
                "total_size": stats.get("total_size", 0),
                "today_calls": stats.get("today_calls", 0),
                "today_size": stats.get("today_size", 0),
                "last_used": stats.get("last_used", datetime.now())
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {
                "total_calls": 0,
                "total_size": 0,
                "today_calls": 0,
                "today_size": 0,
                "last_used": datetime.now()
            }

    def format_stats_message(self, stats: Dict[str, Any]) -> str:
        """Format statistics for display."""
        return (
            "📊 <b>Usage Statistics</b>\n\n"
            f"Today's Usage:\n"
            f"├ API Calls: {stats['today_calls']}\n"
            f"└ Data Processed: {stats['today_size']/1024/1024:.2f} MB\n\n"
            f"Total Usage:\n"
            f"├ API Calls: {stats['total_calls']}\n"
            f"└ Data Processed: {stats['total_size']/1024/1024:.2f} MB\n\n"
            f"Last Used: {stats['last_used'].strftime('%Y-%m-%d %H:%M:%S')}"
        )