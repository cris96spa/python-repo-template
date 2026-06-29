import logging
import os
import random
import string
import threading
from datetime import datetime
from pathlib import Path

from rich import traceback
from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)


class ThreadSafeFileHandler(logging.FileHandler):
    def __init__(self, filename, mode="a", encoding=None, delay=False):
        super(ThreadSafeFileHandler, self).__init__(filename, mode, encoding, delay)
        self._file_access_lock = threading.Lock()

    def emit(self, record):
        with self._file_access_lock:
            super(ThreadSafeFileHandler, self).emit(record)


def generate_log_name() -> str:
    """Generate logname concatenating timestamp, username and a random string."""
    return (
        "_".join(
            [
                (str(datetime.now()).split(".", maxsplit=1)[0].replace(":", ".").replace(" ", "_")),
                os.path.split(os.path.expanduser("~"))[-1],
                "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)),
            ]
        )
        + ".log"
    )


def setup_logger(path_serialization_dir: Path | None = None):
    """Setup the logger to log in the console, and optionally to a file.

    Args:
        path_serialization_dir (Path | None): The directory where the log file will be saved.
            If None, only console logging is configured.
    """
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    traceback.install(show_locals=True)

    fmt = "| %(asctime)s | %(name)s | %(message)s"
    date_format = "[%Y-%m-%d %H:%M:%S]"

    console_columns = int(os.environ.get("COLUMNS", 180))
    console = Console(width=console_columns)

    handlers: list[logging.Handler] = [
        RichHandler(show_time=False, console=console),
    ]

    if path_serialization_dir is not None:
        log_name = generate_log_name()
        handlers.append(
            ThreadSafeFileHandler(os.path.join(path_serialization_dir, log_name), delay=True)
        )

    logging.basicConfig(
        level=loglevel,
        format=fmt,
        datefmt=date_format,
        handlers=handlers,
    )
