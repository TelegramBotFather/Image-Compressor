from pyrogram import Client
from pyrogram.types import Message
from components.keyboards import Keyboards  # Updated import
from utils.decorators import admin_only
from database.mongodb import db
from datetime import datetime, timedelta
import logging
from pyrogram.enums import ParseMode  # Add this import

logger = logging.getLogger(__name__)

@admin_only
async def admin_dashboard(client: Client, message: Message) -> None:
    try:
        dashboard_text = "🔧 <b>Admin Dashboard</b>\n\nSelect an option below:"
        await message.reply_text(
            dashboard_text,
            reply_markup=Keyboards.admin_menu(),  # Updated to use Keyboards class
            parse_mode=ParseMode.HTML  # Updated this line
        )
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        await message.reply_text("❌ An error occurred. Please try again.")

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
