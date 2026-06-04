import logging
from pathlib import Path

from services.log_bus import log_bus


BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "mathesis.log"


class LogBusHandler(logging.Handler):
    """
    Bridges Python logging system -> PyQt log bus (UI)
    """

    def emit(self, record):
        try:
            message = self.format(record)

            parts = message.split("]")

            if len(parts) < 2:
                return

            timestamp = parts[0].replace("[", "").strip()
            rest = parts[1].strip()

            if " - " in rest:
                level, msg = rest.split(" - ", 1)
            else:
                level = record.levelname
                msg = record.getMessage()

            log_bus.log_emitted.emit(
                timestamp,
                level.strip(),
                msg.strip()
            )

        except Exception:
            # Never allow logging failures to crash app
            pass


logger = logging.getLogger("mathesis")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(message)s"
)

# Prevent duplicate handlers when imported multiple times
if not logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    ui_handler = LogBusHandler()
    ui_handler.setLevel(logging.INFO)
    ui_handler.setFormatter(formatter)
    logger.addHandler(ui_handler)

    logger.propagate = False

    logger.info(
        f"Logger initialized | log_file={LOG_FILE}"
    )


def log_event(
    log_level: str,
    event: str,
    **context
):
    """
    Structured log wrapper for Mathesis events.
    Keeps logs consistent across AI, Telegram,
    scheduler, service and UI.
    """

    context_str = " | ".join(
        f"{k}={v}"
        for k, v in context.items()
    )

    message = event

    if context_str:
        message += f" | {context_str}"

    getattr(
        logger,
        log_level.lower(),
        logger.info
    )(message)