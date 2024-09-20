import logging
import logging.handlers
import os
import sys

log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = logging.getLogger("advancedLogger")
logger.setLevel(logging.DEBUG)

log_file = os.path.join(log_directory, "application.log")
handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=7
)
handler.suffix = "%Y-%m-%d"

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def log(message, level="info", *args, **kwargs):
    if level == "debug":
        logger.debug(message, *args, **kwargs)
    elif level == "info":
        logger.info(message, *args, **kwargs)
    elif level == "warning":
        logger.warning(message, *args, **kwargs)
    elif level == "error":
        logger.error(message, *args, **kwargs)
    elif level == "critical":
        logger.critical(message, *args, **kwargs)
    else:
        logger.info(message, *args, **kwargs)
