import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def set_env_vars(project_name: str) -> None:
    """Load environment variables based on the ENV variable."""
    project_root = Path(__file__).parent.parent.parent.resolve()

    # Set default environment variables if .env doesn't exist
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("LOG_FILE_PATH", f"logs/{project_name}.log")
    os.environ.setdefault("ENABLE_CONSOLE_LOGGING", "True")
    os.environ.setdefault("ENABLE_FILE_LOGGING", "True")

    # Path to the minimal .env file (optional)
    minimal_env_path = project_root / ".env"

    # Load the minimal .env file to get the ENV variable (if exists)
    if minimal_env_path.exists():
        load_dotenv(minimal_env_path)

    # Retrieve the ENV variable, default to 'development' if not set
    ENV = os.getenv("ENV", "development").lower()

    # Path to the environment-specific .env file
    env_specific_path = project_root / f".env.{ENV}"

    # Load the environment-specific .env file if it exists
    if env_specific_path.exists():
        load_dotenv(env_specific_path, override=True)


def validate_env_vars() -> None:
    """Validate that all required environment variables are set."""
    required_vars = ["LOG_LEVEL", "LOG_FILE_PATH"]
    if missing_vars := [var for var in required_vars if not os.getenv(var)]:
        raise OSError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


def setup_logging(logger_name: Optional[str] = None) -> logging.Logger:
    """Configure logging based on environment variables."""
    validate_env_vars()

    # Retrieve logging configurations from environment variables
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )
    ENABLE_CONSOLE_LOGGING = os.getenv(
        "ENABLE_CONSOLE_LOGGING", "True"
    ).lower() in ["true", "1", "yes"]
    ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "True").lower() in [
        "true",
        "1",
        "yes",
    ]
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "1048576"))  # 1MB default
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Use the provided logger_name or derive from the project name
    if logger_name is None:
        logger_name = Path(LOG_FILE_PATH).stem

    # Configure the root logger
    logging.basicConfig(level=logging.WARNING)

    # Create and configure logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.propagate = False

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Add handlers
    if ENABLE_CONSOLE_LOGGING:
        console_handler = logging.StreamHandler()
        _configure_handler(console_handler, LOG_LEVEL, formatter, logger)

    if ENABLE_FILE_LOGGING:
        log_dir = Path(LOG_FILE_PATH).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
        )
        _configure_handler(file_handler, LOG_LEVEL, formatter, logger)

    return logger


def _configure_handler(
    handler: logging.Handler,
    level: str,
    formatter: logging.Formatter,
    logger: logging.Logger,
) -> None:
    """Configure and add a handler to the logger."""
    handler.setLevel(getattr(logging, level))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
