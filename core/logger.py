# ============================================================
# MODULE GHI LOG
# ============================================================

import logging
import os
from datetime import datetime
from config import LOG_DIR


def setup_logger(name="AutoGame"):
    """Tạo logger với output ra console và file."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Tránh duplicate handlers
    if logger.handlers:
        return logger

    # Format log
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler - tạo file log mới mỗi ngày
    log_filename = f"autogame_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, log_filename),
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
