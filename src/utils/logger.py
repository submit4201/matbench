
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Constants
LOG_DIR = Path("logs")
APP_LOG_FILE = LOG_DIR / "app.log"
LLM_TRACE_FILE = LOG_DIR / "llm_trace.log"
SERVER_LOG_FILE = LOG_DIR / "server.log"

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

def setup_logging(level=logging.INFO):
    """
    Setup centralized logging with rotation.
    """
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Common Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s'
    )
    
    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # 2. App Log File (Rotating)
    app_handler = RotatingFileHandler(
        APP_LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding='utf-8'
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(level)
    root_logger.addHandler(app_handler)
    
    # 3. LLM Trace Logger (Specific)
    llm_logger = logging.getLogger("src.agents.llm_trace")
    llm_logger.setLevel(logging.DEBUG) # Always capture debug for traces
    llm_handler = RotatingFileHandler(
        LLM_TRACE_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding='utf-8'
    )
    llm_handler.setFormatter(formatter)
    llm_logger.addHandler(llm_handler)
    llm_logger.propagate = False # Don't duplicate to root
    
    # 4. Success Message
    logging.info("==========================================")
    logging.info(f"Logging Initialized. Level: {logging.getLevelName(level)}")
    logging.info(f"Log Directory: {LOG_DIR.absolute()}")
    logging.info("==========================================")

def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(name)

def get_llm_trace_logger():
    """Get the specialized LLM trace logger"""
    return logging.getLogger("src.agents.llm_trace")
