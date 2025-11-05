import logging
from colorama import Fore, Style, init

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.LIGHTBLACK_EX,
        "INFO": Fore.BLUE,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.LIGHTRED_EX,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        grey = Fore.LIGHTBLACK_EX
        white = Fore.WHITE
        asctime = grey + self.formatTime(record, "%Y-%m-%d %H:%M:%S") + Style.RESET_ALL

        # Pick color based on level
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        levelname = color + record.levelname + Style.RESET_ALL
        msg = white + record.getMessage() + Style.RESET_ALL

        return f"{asctime} {levelname}     {msg}"

def get_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = ColoredFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger
