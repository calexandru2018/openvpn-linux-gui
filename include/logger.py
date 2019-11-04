import logging

from logging.handlers import RotatingFileHandler
from include.utils.constants import LOG_FILE

def get_logger():
	"""Create the logger.
	"""
	formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")
	log = logging.getLogger("openvpn-linux-gui")
	log.setLevel(logging.DEBUG)
	#logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

	file_handler = RotatingFileHandler(LOG_FILE, maxBytes=3145728, backupCount=1)
	file_handler.setFormatter(formatter)
	log.addHandler(file_handler)

	return log

log = get_logger()