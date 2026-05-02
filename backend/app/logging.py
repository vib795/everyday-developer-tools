import logging
import os

from .config import settings


def configure_logging() -> logging.Logger:
    os.makedirs(settings.log_directory, exist_ok=True)
    log_file = os.path.join(settings.log_directory, "application.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        force=True,
    )
    logger = logging.getLogger("developer_tools")
    logger.info("Logging system initialized")
    return logger
