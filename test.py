import logging

logFileFormatter = logging.Formatter(
    fmt=f"%(levelname)s %(asctime)s (%(relativeCreated)d) \t %(pathname)s F%(funcName)s L%(lineno)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

class CustomFormatter(logging.Formatter):

    cyan = "\x1b[34m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    orange = "\x1b[38;5;214m"
    red = "\x1b[38;5;202m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"


    FORMATS = {
        logging.DEBUG: cyan + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: orange + format + reset,
        logging.CRITICAL: red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%d-%m-%Y %H:%M:%S')
        return formatter.format(record)

logging.basicConfig(filename="logging.log",
                    filemode='w',
                    format = '%(asctime)s %(levelname)-8s : %(message)s (%(filename)s:%(lineno)d)',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.DEBUG) 

logger = logging.getLogger()
file = logging.FileHandler("logging2.log")
file.setFormatter(CustomFormatter())
logger.addHandler(file)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

logger.debug("2")
logger.info("1")
logger.warning("4")
logger.error("3")
logger.critical("3")


