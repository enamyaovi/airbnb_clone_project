import logging
import os

os.makedirs("logs", exist_ok=True)

# Set up logger
logger = logging.getLogger("seed_logger")
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(filename='logs/app.log', mode='a', encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Set formatter
formatter = logging.Formatter("{asctime} - {levelname}: {message}", style="{")
file_handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(file_handler)
