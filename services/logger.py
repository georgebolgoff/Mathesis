import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("mathesis")

logger.setLevel(logging.INFO)

if not logger.handlers:

    formatter = logging.Formatter(
        "[%(asctime)s] "
        "%(levelname)s - "
        "%(message)s"
    )

    file_handler = logging.FileHandler("logs/mathesis.log", encoding="utf-8")

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    print("LOGGER INITIALIZED")

