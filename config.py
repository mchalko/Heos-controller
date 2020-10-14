from structures import *
import json

CONF_FILE = "/device.conf"  # default config file
__cache = None  # cache to prevent unnecessary loading


def saveconfig(config):
    """
    Saves configuration into a file
    :param config: Configuration object
    """
    with open(CONF_FILE, "w") as f:
        json.dump(config.todict, f)
        global __cache
        __cache = config


def loadconfig(force=False):
    """
    read params from config file. If called multiple times returns cached values from the file
    :param force: force reading the file instead of using cache
    :return: Configuration object. On fail return default config
    """
    global __cache
    if not force and __cache:
        return __cache

    try:
        with open(CONF_FILE) as f:
            config = Configuration(**json.load(f))
            __cache = config
            return config
    except OSError:  # file doesn't exists
        return Configuration()
