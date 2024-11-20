from pyrogram import Client
from pyrogram.types import Message
from utils.decorators import admin_only
from database.mongodb import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@admin_only
async def detailed_stats(client: Client, message: Message) -> None:
    try:
        # Time periods
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        this_month = today.replace(day=1)
        
        # Get statistics
        stats = {
            "users": {
                "total": await db.users.count_documents({}),
                "today": await db.users.count_documents({"joined_date": {"$gte": today}}),
                "yesterday": await db.users.count_documents({
                    "joined_date": {
                        "$gte": yesterday,
                        "$lt": today
                    }
                }),
                "this_month": await db.users.count_documents({
                    "joined_date": {"$gte": this_month}
                })
            },
            "compressions": {
                "total": await db.usage_stats.count_documents({}),
                "today": await db.usage_stats.count_documents({
                    "date": {"$gte": today}
                }),
                "yesterday": await db.usage_stats.count_documents({
                    "date": {
                        "$gte": yesterday,
                        "$lt": today
                    }
                }),
                "this_month": await db.usage_stats.count_documents({
                    "date": {"$gte": this_month}
                })
            }
        }

        # Format message
        stats_text = (
            "📊 <b>Detailed Statistics</b>\n\n"
            f"👥 <b>Users</b>\n"
            f"├ Total: {stats['users']['total']:,}\n"
            f"├ Today: {stats['users']['today']:,}\n"
            f"├ Yesterday: {stats['users']['yesterday']:,}\n"
            f"└ This Month: {stats['users']['this_month']:,}\n\n"
            f"🖼 <b>Compressions</b>\n"
            f"├ Total: {stats['compressions']['total']:,}\n"
            f"├ Today: {stats['compressions']['today']:,}\n"
            f"├ Yesterday: {stats['compressions']['yesterday']:,}\n"
            f"└ This Month: {stats['compressions']['this_month']:,}\n\n"
            f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await message.reply_text(stats_text, parse_mode="html")

    except Exception as e:
        logger.error(f"Error in detailed stats: {str(e)}")
        await message.reply_text("❌ An error occurred while fetching statistics.")
