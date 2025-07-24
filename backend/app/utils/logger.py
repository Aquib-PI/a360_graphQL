import logging
from pythonjsonlogger import jsonlogger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Returns a configured JSON logger.
    - name: logger name (module or app-wide).
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = '%(asctime)s %(levelname)s %(name)s %(message)s'
        formatter = jsonlogger.JsonFormatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Default logger for the application
logger = get_logger("kpi_dashboard") 