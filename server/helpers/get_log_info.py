import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_log_info(log_id):
    def log_info(msg, *args):
        logger.info(log_id + " " + msg, *args)

    return log_info
