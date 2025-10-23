import logging
from colorama import Fore, Style, init

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        grey = Fore.LIGHTBLACK_EX
        blue = Fore.BLUE
        white = Fore.WHITE

        asctime = grey + self.formatTime(record, "%Y-%m-%d %H:%M:%S") + Style.RESET_ALL
        levelname = blue + record.levelname + Style.RESET_ALL
        msg = white + record.getMessage() + Style.RESET_ALL

        return f"{asctime} {levelname} {msg}"


def get_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = ColoredFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
