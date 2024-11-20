from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.decorators import admin_only
from database.mongodb import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@admin_only
async def admin_dashboard(client: Client, message: Message) -> None:
    try:
        # Get statistics
        total_users = await db.users.count_documents({})
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users = await db.users.count_documents({"joined_date": {"$gte": today}})
        
        # Get usage statistics
        total_compressions = await db.usage_stats.count_documents({})
        today_compressions = await db.usage_stats.count_documents({
            "date": {"$gte": today}
        })

        dashboard_text = (
            "📊 <b>Admin Dashboard</b>\n\n"
            f"👥 <b>Users</b>\n"
            f"├ Total Users: {total_users:,}\n"
            f"└ New Today: {new_users:,}\n\n"
            f"🖼 <b>Compressions</b>\n"
            f"├ Total: {total_compressions:,}\n"
            f"└ Today: {today_compressions:,}\n\n"
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        buttons = [
            [
                InlineKeyboardButton("📊 Detailed Stats", callback_data="admin_stats"),
                InlineKeyboardButton("👥 User List", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
                InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
            ]
        ]

        await message.reply_text(
            dashboard_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="html"
        )

    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        await message.reply_text("❌ An error occurred while loading the dashboard.")

@admin_only
async def broadcast_message(client: Client, message: Message) -> None:
    """Broadcast message to all users."""
    try:
        # Get message to broadcast
        if not message.reply_to_message:
            await message.reply_text(
                "⚠️ Please reply to the message you want to broadcast."
            )
            return

        # Get all users
        users = await db.users.find({}).to_list(length=None)
        
        # Initialize counters
        success = 0
        failed = 0
        
        # Send status message
        status_msg = await message.reply_text("📤 Broadcasting message...")
        
        # Broadcast message
        for user in users:
            try:
                await message.reply_to_message.copy(user["user_id"])
                success += 1
            except Exception:
                failed += 1
            
            # Update status every 20 users
            if (success + failed) % 20 == 0:
                await status_msg.edit_text(
                    f"📤 Broadcasting message...\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"📊 Progress: {((success + failed)/len(users))*100:.1f}%"
                )
        
        # Send final status
        await status_msg.edit_text(
            f"📤 Broadcast completed!\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}\n"
            f"👥 Total Users: {len(users)}"
        )

    except Exception as e:
        logger.error(f"Error in broadcast: {str(e)}")
        await message.reply_text("❌ An error occurred while broadcasting.")
