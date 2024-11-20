from datetime import datetime
from database.user_db import save_user_log
import logging

logger = logging.getLogger(__name__)

class UserLogger:
    @staticmethod
    async def log_user_action(
        user_id: int,
        action: str,
        details: dict = None
    ) -> None:
        """Log user actions."""
        try:
            log_data = {
                "user_id": user_id,
                "action": action,
                "timestamp": datetime.now(),
                "details": details or {}
            }
            await save_user_log(log_data)
        except Exception as e:
            logger.error(f"Error logging user action: {str(e)}")