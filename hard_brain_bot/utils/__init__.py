import logging


def setup_logging(name: str, log_path: str, format_string: str, level: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.getLevelName(level))
    handler = logging.FileHandler(filename=log_path, encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(handler)
