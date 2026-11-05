import logging

from config import LOG_DIR

# Anchored to the project (see config.py), not to whatever folder the program was started from.
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("Autotrader")
logger.setLevel(logging.DEBUG)

# Handle all output here. Without this, each record is also passed up to the root logger,
# which printed every console line twice (and exposed other libraries' debug output).
logger.propagate = False

formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

# Only attach handlers once, even if this module is imported or reloaded more than once.
if not logger.handlers:
	application_handler = logging.FileHandler(LOG_DIR / "application.log")
	application_handler.setLevel(logging.DEBUG)
	application_handler.setFormatter(formatter)

	error_handler = logging.FileHandler(LOG_DIR / "error.log")
	error_handler.setLevel(logging.ERROR)
	error_handler.setFormatter(formatter)

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_handler.setFormatter(formatter)

	logger.addHandler(application_handler)
	logger.addHandler(error_handler)
	logger.addHandler(console_handler)
