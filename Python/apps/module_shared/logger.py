import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_DIR = "/apps/logs"

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    app_name: str,
    default_level: str = "INFO",
    module_levels: dict[str, str] | None = None,
) -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(_FORMAT, _DATE_FORMAT))
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        f"{LOG_DIR}/{app_name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(logging.Formatter(_FORMAT, _DATE_FORMAT))
    root.addHandler(file_handler)

    log_levels = logging.getLevelNamesMapping()
    root.setLevel(log_levels.get(default_level.upper(), logging.INFO))

    if module_levels:
        for name, level in module_levels.items():
            logging.getLogger(name).setLevel(log_levels.get(level.upper(), logging.INFO))
