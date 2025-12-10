import json
import logging
import os
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
        # Let the base class handle the rotation/rename
        super().rotate(source, dest)
        # Then compress the rotated file (dest)
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
    def __init__(self, datefmt: str | None = None):
        super().__init__(datefmt=datefmt)

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

def _build_log_filename(category: str) -> Path:
    log_dir = _ensure_log_dir(category)
    current_date = datetime.now().strftime("%m-%d-%Y--%H")
    return log_dir / f"{category}-{current_date}.log"

def _create_console_handler(formatter: logging.Formatter) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler

def _create_file_handler(category: str) -> logging.Handler:
    base_filename = _build_log_filename(category)
    handler = CompressedTimedRotatingFileHandler(
        filename=base_filename,
        when=ROTATION_WHEN,
        interval=ROTATION_INTERVAL,
        backupCount=MAX_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(JSONFormatter())
    return handler

def setup_logger(name: str, category: str = "general", level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with:
    1. Console Handler (Standard Output)
    2. TimedRotatingFileHandler (Per category, rotated every 2h, zipped)
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
    )

    logger.addHandler(_create_console_handler(formatter))
    logger.addHandler(_create_file_handler(category))
    logger.propagate = False
    return logger

# -- Global/Default Setup for Server --
_ROOT_LOGGER: Optional[logging.Logger] = None

def get_logger(name: str, category: str | None = None) -> logging.Logger:
    """
    Factory to get or create a logger.
    If category is provided, ensures a file handler for that category exists.
    """
    global _ROOT_LOGGER
    if _ROOT_LOGGER is None:
        _ROOT_LOGGER = setup_logger("root", "general")

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
