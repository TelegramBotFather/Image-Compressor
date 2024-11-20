import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with a rotating file handler.

    Args:
        name (str): Name of the logger.
        log_file (str): Path to the log file.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

# Initialize loggers for different modules
file_handler_logger = setup_logger('handlers.file_handler', 'logs/file_handler.log')
url_handler_logger = setup_logger('handlers.url_handler', 'logs/url_handler.log')
broadcast_logger = setup_logger('commands.broadcast', 'logs/broadcast.log')
api_handler_logger = setup_logger('api_management.api_handler', 'logs/api_handler.log')
user_db_logger = setup_logger('database.user_db', 'logs/user_db.log')

# You can initialize more loggers as needed for other modules
