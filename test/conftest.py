import pytest
import logging
import os
from pathlib import Path
from datetime import datetime
from src.utils.logger import CompressedTimedRotatingFileHandler

# Define test log directory
TEST_LOG_DIR = Path(".test/.log")
TEST_LOG_DIR.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """
    Configures logging for the test session.
    Logs are directed to .test/.log/TestRun-MM-DD-YYYY--HH.log
    """
    # Create valid filename
    current_date = datetime.now().strftime("%m-%d-%Y--%H")
    log_file = TEST_LOG_DIR / f"TestRun-{current_date}.log"
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication during tests
    # (handling cautiously to not break pytest's own capturing)
    # root_logger.handlers = [] 
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
    )
    
    # File Handler
    file_handler = CompressedTimedRotatingFileHandler(
        filename=log_file,
        when='H',
        interval=2,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    logging.info("----------------------------------------------------------------")
    logging.info(f"Test Session Started. Logging to {log_file}")
    logging.info("----------------------------------------------------------------")
    
    yield
    
    logging.info("----------------------------------------------------------------")
    logging.info("Test Session Ended.")
    logging.info("----------------------------------------------------------------")

@pytest.fixture
def capture_logs(caplog):
    """Fixture to help assert on logs"""
    caplog.set_level(logging.INFO)
    return caplog
