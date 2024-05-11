import logging


def setup_logging(name: str, level: str, log_path: str | None = None, format_string: str | None = None):
    """
    Setup logging to a log file. If no log path is set, logs to sys.stderr
    :type name: Name to user for the logger
    :param level: Level of logging (CRITICAL, ERROR, WARNING, INFO, DEBUG)
    :param log_path: Path to the log file to write to
    :param format_string: Format string for the log events
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.getLevelName(level))
    if log_path:
        handler = logging.FileHandler(filename=log_path, encoding="utf-8", mode="w")
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(handler)
