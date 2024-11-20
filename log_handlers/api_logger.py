from datetime import datetime
from database.api_db import save_api_log
import logging

logger = logging.getLogger(__name__)

class APILogger:
    @staticmethod
    async def log_api_call(
        user_id: int,
        api_key: str,
        success: bool,
        response: dict = None
    ) -> None:
        """Log API calls."""
        try:
            log_data = {
                "user_id": user_id,
                "api_key": api_key,
                "success": success,
                "response": response or {},
                "timestamp": datetime.now()
            }
            await save_api_log(log_data)
        except Exception as e:
            logger.error(f"Error logging API call: {str(e)}")