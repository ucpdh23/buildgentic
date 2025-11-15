import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from .server import run_server

load_dotenv()


# Logging configuration
LOG_PATH = os.getenv("LOG_PATH", "logs/app.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

log_path = Path(LOG_PATH).expanduser()
log_dir = log_path.parent
try:
    log_dir.mkdir(parents=True, exist_ok=True)
except Exception:
    # If we cannot create the directory, fall back to current directory
    log_path = Path("app.log")

logger = logging.getLogger("buildgentic")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Stream (console) handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# File handler (best-effort)
try:
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning("Could not create file handler for logs at %s: %s", log_path, e)


def startup():
    logger.info("Starting startup...")

    run_server(host="0.0.0.0", port=8008)
    
    logger.info("Finalizing startup.")


if __name__ == "__main__":
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (KeyboardInterrupt).")
    except Exception as e:
        logger.exception("Unhandled exception in main: %s", e)
    finally:
        # Ensure handlers are flushed and closed
        handlers = logger.handlers[:]
        for h in handlers:
            try:
                h.flush()
                h.close()
            except Exception:
                pass
            logger.removeHandler(h)
