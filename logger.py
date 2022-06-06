from dotenv import load_dotenv
import os
import logging
import ecs_logging

load_dotenv()
LOG_FILE = os.environ["LOG_FILE"]

log = None


def get_logger(name):
    global log
    if log:
        return log

    log = logging.getLogger(name)
    logging.basicConfig(level=logging.DEBUG)
    handler = logging.FileHandler(filename=LOG_FILE, mode="a")
    handler.setFormatter(ecs_logging.StdlibFormatter())
    log.addHandler(handler)
    return log
