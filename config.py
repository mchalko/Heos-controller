"""
Example of usage of config file:
AP:CONFIG:{IP},{Mask}
AP:SSID:{Name of the AP}
AP:PASSWORD:{password of the AP}
ETH:ENABLE:{True/False}
ETH:CONFIG:{IP},{Mask},{Gate} (dhcp will be used if this parameter is omitted)
WLAN:ENABLE:{True/False}
WLAN:profile:{SSID};{BSSID}(optional);{password};{{IP},{Mask},{Gate}}(optional)
HEOS:NAME:{heos name}
HEOS:USER:{user name}
HEOS:PASSWORD:{password}

Blank lines or lines starting with '#' will be ignored
File is overwritten if profile is saved
"""

from structures import *
SEP_VAL = ';'
SEP_ATTR = ':'
SEL_AP = "AP"
SEL_ETH = "ETH"
SEL_WLAN = "WLAN"
SEL_HEOS = "HEOS"
ATTR_NET = "NET"
ATTR_PROFILE = "PROFILE"
ATTR_ENABLE = "ENABLE"
ATTR_NAME = "NAME"
ATTR_USER = "USER"
ATTR_PASSWORD = "PASSWORD"
ATTR_SSID = "SSID"
CHAR_NEWLINE = '\n'

__cache = None  # cache to prevent unnecessary loading


def __toString(selector, attribute, value):
    return selector + SEP_ATTR + attribute + SEP_ATTR + value + CHAR_NEWLINE


def saveconfig(config, file):
    """
    Saves configuration into a file
    :param config: Configuration object
    :param file: name of a file
    """
    with open(file, "w") as f:
        # HEOS settings
        f.write(__toString(SEL_HEOS, ATTR_NAME, config.HEOS.name))
        f.write(__toString(SEL_HEOS, ATTR_USER, config.HEOS.user))
        f.write(__toString(SEL_HEOS, ATTR_PASSWORD, config.HEOS.password))
        # AP settings
        f.write(__toString(SEL_AP, ATTR_SSID, config.AP.ssid))
        f.write(__toString(SEL_AP, ATTR_PASSWORD, config.AP.password))
        f.write(__toString(SEL_AP, ATTR_NET, config.AP.net.getstring()))
        # ETH settings
        f.write(__toString(SEL_ETH, ATTR_ENABLE, str(config.ETH.enabled)))
        f.write(__toString(SEL_ETH, ATTR_NET, config.ETH.net.getstring()))
        # WLAN settings
        f.write(__toString(SEL_WLAN, ATTR_ENABLE, str(config.WLAN.enabled)))
        for entry in config.WLAN.profiles:
            # skip saving profile that contains value separator as value to avoid problems while parsing
            if any(SEP_VAL in p for p in entry.tolist()):
                continue;
            f.write(__toString(SEL_WLAN, ATTR_PROFILE, SEP_VAL.join(entry.tolist())))

        f.close()

        global __cache
        __cache = config


def loadconfig(config, force=False):
    """
    read params from config file. If called multiple times returns cached values from the file
    :param config: file name
    :param force: force reading the file instead of using cache
    :return: Configuration object on success, None on fail
    """
    global __cache
    if not force and __cache:
        return __cache

    try:
        with open(config) as file:
            result = Configuration()
            lines = file.readlines()

            for line in lines:
                line = line.lstrip().rstrip('\n').rstrip('\r')  # remove trailing white spaces and endLine
                if not len(line) or line[0] == '#':  # skip blank lines and lines starting with '#'
                    continue
                # parse file
                parts = line.split(SEP_ATTR)
                if len(parts) < 3:  # every line consists of selector, attribute and value
                    raise OSError  # file is corrupt
                selector = parts[0].upper()
                attribute = parts[1].upper()
                value = SEP_ATTR.join(parts[2:])

                if selector == SEL_HEOS:  # heos settings
                    if attribute == ATTR_NAME:
                        result.HEOS.name = value
                    elif attribute == ATTR_USER:
                        result.HEOS.user = value
                    elif attribute == ATTR_PASSWORD:
                        result.HEOS.password = value
                elif selector == SEL_WLAN:  # wlan settings
                    if attribute == ATTR_ENABLE:
                        result.WLAN.enabled = value.lower() == "true"
                    if attribute == ATTR_PROFILE:
                        profile = value.split(SEP_VAL)
                        if len(profile) != 4:  # WLAN profile has 4 parts SSID;password;BSSID;IPconfig
                            continue  # ignore invalid profile
                        result.WLAN.profiles.append(Profile(*profile))
                elif selector == SEL_ETH:  # eth settings
                    if attribute == ATTR_NET:
                        result.ETH.net = Net(value)
                    elif attribute == ATTR_ENABLE:
                        result.ETH.enabled = value.lower() == "true"
                elif selector == SEL_AP:  # ap settings
                    if attribute == ATTR_SSID:
                        result.AP.ssid = value
                    elif attribute == ATTR_PASSWORD:
                        result.AP.password = value
                    elif attribute == ATTR_NET:
                        result.AP.net = Net(value)

            __cache = result
            return result
    except OSError:
        return None
