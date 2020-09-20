"""
Example of usage of link config file:
AP:CONFIG:{IP},{Mask},{Gate(ignored)}
AP:SSID:{Name of the AP}
AP:PASSWORD:{password of the AP}
LAN:ENABLE:{True/False}
LAN:CONFIG:{IP},{Mask},{Gate} (dhcp will be used if this parameter is emited)
WLAN:ENABLE:{True/False}
WLAN:profile:{SSID};{BSSID}(optional);{password};{{IP},{Mask},{Gate}}(optional)

Example of usage of heos config file:
NAME:{heos name}
USER:{user name}
PASSWORD:{password}

Blank lines or lines starting with '#' will be ignored
File is overwritten if profile is saved
"""

SEP_VAL = ';'
SEP_IP = ','
SEP_ATTR = ':'
SEL_AP = "AP"
SEL_LAN = "LAN"
SEL_WLAN = "WLAN"
ATTR_CONF = "CONFIG"
ATTR_PROFILE = "PROFILE"
ATTR_ENABLE = "ENABLE"
ATTR_NAME = "NAME"
ATTR_USER = "USER"
ATTR_PASSWORD = "PASSWORD"
ATTR_SSID = "SSID"
CHAR_NEWLINE = '\n'


class Profile(object):
    """
    Class for storing wlan profile info
    """
    def __init__(self, ssid="", password="", bssid="", conf=""):
        self.ssid = ssid
        self.bssid = bssid
        self.password = password
        self.conf = conf

    def __str__(self):
        return "[\"" + self.ssid + "\",\"" + self.password + "\",\"" + self.bssid + "\",\"" + self.conf + "\"]"

    def __repr__(self):
        return self.__str__()


class Netconfig(object):
    """
    Class for storing network info
    """
    def __init__(self): # init default values
        self.AP_ssid = "ReCo"
        self.AP_pass = "12345678"
        self.AP_conf = "192.168.0.1,255.255.255.0,192.168.0.1"
        self.ETH_en = False
        self.ETH_conf = ""
        self.WLAN_en = False
        self.WLAN_profiles = []
    def __str__(self):
        val = "AP["+self.AP_ssid+";"+self.AP_pass+";"+self.AP_conf+"]\n"
        val += "ETH["+str(self.ETH_en)+";"+self.ETH_conf +"]\n"
        val += "WLAN["+str(self.WLAN_en)+";"+str(self.WLAN_profiles)+"]"
        return val
    def __repr__(self):
        return self.__str__()

class Heosconfig(object):
    """
    Class for storing heos info
    """
    def __init__(self, name = "", user = "", passw = ""):
        self.name = name
        self.user = user
        self.password = passw
        
    def __str__(self):
        return "["+self.name+":"+self.user+":"+self.password+"]"
    def __repr__(self):
        return self.__str__()


def iptostring(ip, mask, gate=None):
    """
    Converts ip configuration - list of ip addresses into string
    If gate isn't specified, uses IP param as the gate.
    """
    return ip + SEP_IP + mask + SEP_IP + gate if gate else ip


def stringtoip(string):
    """
    Converts string with IP configuration into a list of IP addresses
    :param string: ip config
    :return: tuple (IP, mask, gate)
    """
    if not string:
        return None
    parts = string.split(SEP_IP)
    if parts == 2:
        return (parts[0], parts[1], parts[0])
    elif parts == 3:
        return tuple(parts)
    else:
        return None


# caches to prevent unnecessary loading
__cache_heosconfig = None
__cache_netconfig = None


def save_heosconfig(config, file):
    """
    Saves heos configuration into a file
    :param config: Heosconfig object
    :param file: name of a file
    """
    with open(file, "w") as f:
        f.write(ATTR_NAME + SEP_ATTR + config.name + CHAR_NEWLINE)
        f.write(ATTR_USER + SEP_ATTR + config.user + CHAR_NEWLINE)
        f.write(ATTR_PASSWORD + SEP_ATTR + config.password + CHAR_NEWLINE)
        f.close()

        global __cache_heosconfig
        __cache_heosconfig = config


def save_netconfig(config, file):
    """
    Saves network configuration into a file
    :param config: Netconfig object
    :param file: name of a file
    """
    with open(file, "w") as f:
        f.write(SEL_AP + SEP_ATTR + ATTR_SSID + SEP_ATTR + config.AP_ssid + CHAR_NEWLINE)
        f.write(SEL_AP + SEP_ATTR + ATTR_PASSWORD + SEP_ATTR + config.AP_pass + CHAR_NEWLINE)
        f.write(SEL_AP + SEP_ATTR + ATTR_CONF + SEP_ATTR + config.AP_conf + CHAR_NEWLINE)
        f.write(SEL_LAN + SEP_ATTR + ATTR_ENABLE + SEP_ATTR + str(config.ETH_en) + CHAR_NEWLINE)
        f.write(SEL_LAN + SEP_ATTR + ATTR_CONF + SEP_ATTR + config.ETH_conf + CHAR_NEWLINE)

        f.write(SEL_WLAN + SEP_ATTR + ATTR_ENABLE + SEP_ATTR + str(config.WLAN_en) + CHAR_NEWLINE)
        for entry in config.WLAN_profiles:
            f.write(SEL_WLAN + SEP_ATTR + ATTR_PROFILE + SEP_ATTR +
                    entry.ssid + SEP_VAL +
                    entry.password + SEP_VAL +
                    entry.bssid + SEP_VAL +
                    entry.conf + CHAR_NEWLINE)
        f.close()

        global __cache_netconfig
        __cache_netconfig = config


def load_heosconfig(config, force=False):
    """
    read params of heos from config file. If called multiple times returns cached values from the file
    :param config: file name
    :param force: force reading the file instead of using cache
    :return: Heosconfig object on success, None on fail
    """
    global __cache_heosconfig
    if not force and __cache_heosconfig:
        return __cache_heosconfig

    try:
        with open(config) as file:
            result = Heosconfig()
            lines = file.readlines()
            for line in lines:
                line = line.lstrip().rstrip('\n').rstrip('\r')  # remove trailing white spaces and endLine
                if not len(line) or line[0] == '#':  # skip blank lines and lines starting with '#'
                    continue
                # parse file
                parts = line.split(SEP_ATTR)
                if len(parts) < 2:  # every line consists of 1 attribute and value
                    raise OSError  # file is corrupt
                attribute = parts[0].upper()
                value = SEP_ATTR.join(parts[1:])  # join the remaining parts (in case other field contained separator)

                if attribute == ATTR_NAME:
                    result.name = value
                elif attribute == ATTR_USER:
                    result.user = value
                elif attribute == ATTR_PASSWORD:
                    result.password = value
                    
            __cache_heosconfig = result
            return result
    except OSError:
        return None


def load_netconfig(config, force=False):
    """
    reads params of network configuration file. If called multiple times returns cached values from the file
    :param config: file name
    :param force: force reading the file instead of using cache
    :return: Netconfig object on success, None on fail
    """
    global __cache_netconfig
    if not force and __cache_netconfig:
        return __cache_netconfig
        
    try:
        with open(config) as file:
            result = Netconfig()
            lines = file.readlines()
            for line in lines:
                line = line.lstrip().rstrip('\n').rstrip('\r')  # remove trailing white spaces and endLine
                if not len(line) or line[0] == '#':  # skip lines starting with '#' and blank lines
                    continue
                # parse file
                parts = line.split(SEP_ATTR)
                if len(parts) < 3:  # every line consists of 1 selector, 1 attribute and value
                    raise OSError  # file is corrupt
                selector = parts[0].upper()
                attribute = parts[1].upper()
                value = SEP_ATTR.join(parts[2:])

                if selector == SEL_WLAN:
                    if attribute == ATTR_ENABLE:
                        result.WLAN_en = value.lower() == "true"
                    if attribute == ATTR_PROFILE:
                        profile = value.split(SEP_VAL)
                        if len(profile) != 4:  # WLAN profile has 4 parts SSID;BSSID;password;IPconfig
                            continue  # ignore invalid profile
                        result.WLAN_profiles.append(Profile(*profile))
                elif selector == SEL_LAN:
                    if attribute == ATTR_CONF:
                        result.ETH_conf = value
                    elif attribute == ATTR_ENABLE:
                        result.ETH_en = value.lower() == "true"
                elif selector == SEL_AP:
                    if attribute == ATTR_SSID:
                        result.AP_ssid = value
                    elif attribute == ATTR_PASSWORD:
                        result.AP_pass = value
                    elif attribute == ATTR_CONF:
                        result.AP_conf = value
                        
            __cache_netconfig = result
            return result
    except OSError:
        return None
