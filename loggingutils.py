import logging
logger_initialized = False
log_level = logging.DEBUG
log_format = ('%(levelname)s:%(module)s:%(pathname)s:%(lineno)d: ' +
              '%(message)s')


def initialize_logger():
    if not logger_initialized:
        logger = logging.getLogger()
        logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=log_format))
        logger.addHandler(handler)

    else:
        logging.warn("root logger already initialized")