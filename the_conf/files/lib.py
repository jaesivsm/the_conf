import os.path
import logging

logger = logging.getLogger(__name__)


def get_fd(path, mode):
	try:
		fd = open(path, mode)
		logger.info('will use conf from %r', path)
		return fd
	except PermissionError:
		if os.path.exists(path):
			logger.warn('permission denied on %s(%s)', path, mode)
	except FileNotFoundError:
		pass
