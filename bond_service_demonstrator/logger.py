import logging
import os
from logging.handlers import RotatingFileHandler


# Nastavení loggeru
def setup_logging() -> None:
    """
    Configures the logging system to log to both a file in the 'logs' directory
    and the console.
    The logs are stored in the 'logs/bsd_main.log' file, and logs are also
    shown in the console.
    """
    # Ensure that the 'logs' directory exists
    log_dir: str = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)  # Create the directory if it doesn't exist

    log_file: str = os.path.join(log_dir, "bsd_main.log")

    # Set up logging configuration with rotation
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5
            ),  # Log to file with rotation
            logging.StreamHandler(),  # Log to console
        ],
    )


# A reference to the root logger
logger: logging.Logger = logging.getLogger(__name__)
