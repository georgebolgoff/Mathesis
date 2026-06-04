import logging
import os

from services.log_bus import log_bus

os.makedirs("logs", exist_ok=True)


class LogBusHandler(logging.Handler):
    """
    Bridges Python logging system -> PyQt log bus (UI)
    """

    def emit(self, record):
        try:
            #format message exactly like logger output
            message = self.format(record)

            # extract timestamp from formatted string
            # format: [2026-06-03 12:00:00] INFO - message

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
            # Never crash app because of logging
            pass



logger = logging.getLogger("mathesis")

logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(message)s"
)

# FILE HANDLER 
file_handler = logging.FileHandler(
    "logs/mathesis.log",
    encoding="utf-8"
)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#UI HANLDER (NEW)
ui_handler = LogBusHandler()
ui_handler.setLevel(logging.INFO)
ui_handler.setFormatter(formatter)
logger.addHandler(ui_handler)


def log_event(log_level: str, event: str,**context):
    """
    Structured log wrapper for Mathesis events.
    Keeps logs consistent acroos AI, Telegram, scheduler, UI
    """

    context_str = " | ".join(f"{k}={v}" for k, v in context.items())

    message = f"{event}"

    if context_str:
        message += f" | {context_str}"


    getattr(logger, log_level.lower(), logger.info)(message)



