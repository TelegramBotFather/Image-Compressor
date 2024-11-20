from pyrogram import Client
from pyrogram.types import Message
from api_management.usage_tracker import UsageTracker
import logging

logger = logging.getLogger(__name__)

async def stats_command(client: Client, message: Message) -> None:
    try:
        user_id = message.from_user.id
        tracker = UsageTracker()
        stats = await tracker.get_user_stats(user_id)

        stats_text = (
            "📊 <b>Your Usage Statistics</b>\n\n"
            f"Today's Usage:\n"
            f"├ Files: {stats['today_files']}\n"
            f"└ Data: {stats['today_size']/1024/1024:.2f} MB\n\n"
            f"Total Usage:\n"
            f"├ Files: {stats['total_files']}\n"
            f"└ Data: {stats['total_size']/1024/1024:.2f} MB\n\n"
            f"Last Used: {stats['last_used'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await message.reply_text(
            stats_text,
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Error in stats command: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")