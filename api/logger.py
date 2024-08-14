import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

logger.handlers[0].setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
