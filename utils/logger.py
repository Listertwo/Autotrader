import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Autotrader")

formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

application_handler = logging.FileHandler('logs/application.log')
application_handler.setLevel(logging.DEBUG)
application_handler.setFormatter(formatter)

error_handler = logging.FileHandler('logs/error.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(application_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)