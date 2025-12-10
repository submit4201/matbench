import json
import logging
import zipfile
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional

# Constants
BASE_LOG_DIR = Path(".log")
MAX_BACKUP_COUNT = 24  # Keep last 24 rotated files (2 days worth if 2h rotation)
ROTATION_INTERVAL = 2  # Hours
ROTATION_WHEN = 'H'    # Hours

class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Extended TimedRotatingFileHandler that zips the rotated log file.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)

    def rotate(self, source: str, dest: str):
        """
        Rotates the source log file to dest, then zips dest.
        """
        # 1. Perform standard rotation (rename source -> dest)
        if os.path.exists(source):
            try:
                os.rename(source, dest)
            except OSError:
                # Fallback for Windows if file is locked
                pass
        
        # 2. Compress the rotated file
        self.compress_log(dest)

    def compress_log(self, file_path: str):
        """
        Compresses the given log file into a zip archive and removes the original.
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return

            zip_name = f"{file_path}.zip"
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, file_path_obj.name)
            
            # Remove original log file after zipping
            os.remove(file_path)
        except Exception as e:
            # Fallback: print to stderr if logging fails (since this IS the logging system)
            print(f"Failed to compress log {file_path}: {e}")

class JSONFormatter(logging.Formatter):
    """
    Formatter to output logs in JSON format.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def _ensure_log_dir(category: str = "general") -> Path:
    """Correctly creates subdirectory for logs: logs/server/, logs/agents/, etc."""
    log_dir = BASE_LOG_DIR / category
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def setup_logger(name: str, category: str = "general", level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with:
    1. Console Handler (Standard Output)
    2. TimedRotatingFileHandler (Per category, rotated every 2h, zipped)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File Handler
    log_dir = _ensure_log_dir(category)
    # Filename format: Category-Date.log (Rotation adds timestamp suffix)
    # Actually, TimedRotatingFileHandler handles the suffix. 
    # We'll stick to a base name "service.log" and let it rotate to "service.log.2023-..."
    # User requested: "logs named by date and time with a discriptor... GameMaster-MM-DD-YYYY--HH.log"
    # To achieve exact naming at START time is tricky with rotation, usually rotation APPENDS date.
    # We will use a base name that includes the startup date, and allow rotation to append hours.
    
    current_date = datetime.now().strftime("%m-%d-%Y--%H")
    base_filename = log_dir / f"{category}-{current_date}.log"

    file_handler = CompressedTimedRotatingFileHandler(
        filename=base_filename,
        when=ROTATION_WHEN,
        interval=ROTATION_INTERVAL,
        backupCount=MAX_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(JSONFormatter('%(asctime)s'))
    
    # Custom namer for the rotated file to match user format better?
    # Default is filename.YYYY-MM-DD_HH-MM
    # We will accept standard rotation suffix for now to ensure robustness.
    
    logger.addHandler(file_handler)
    logger.propagate = False  # Prevent double logging if attached to root

    return logger

# -- Global/Default Setup for Server --
ROOT_LOGGER = setup_logger("root", "general")

def get_logger(name: str, category: str = None) -> logging.Logger:
    """
    Factory to get or create a logger.
    If category is provided, ensures a file handler for that category exists.
    """
    # Simple mapping based on name if category not provided
    if not category:
        if "server" in name or "uvicorn" in name:
            category = "server"
        elif "agent" in name:
            category = "agents"
        elif "engine" in name:
            category = "engine"
        else:
            category = "general"
            
    return setup_logger(name, category)
