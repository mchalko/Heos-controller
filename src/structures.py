import re

DNS_DEFAULT = "8.8.8.8"
SEP_IP = ","


class Net(object):
    """
    class for storing ip configuration of a network
    """

    def __init__(self, string="", net=[]):
        """
        initialize Net object
        :param string: create net object from string
        :param net: create net object from net
        """
        if len(net):
            self.__conf = Net.stringtonet(SEP_IP.join(net))
        else:
            self.__conf = Net.stringtonet(string)
        # contains ip tuples
        if net and any(not Net.isip(ip) for ip in net):
            raise ValueError  # raise error if invalid ip detected

    def getnet(self):
        return self.__conf

    def __repr__(self):
        return str(self.__conf)

    def __str__(self):
        return str(self.__conf)

    @staticmethod
    def isip(ip):
        """
        checks whether string contains valid IP address
        :param ip: ip to check
        :return: True if string contains valid ip
        """
        if not ip:
            return False

        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            if any(int(p) > 255 for p in parts):
                return False
        except ValueError:
            return False

        return True

    @staticmethod
    def stringtonet(string):
        """
        Converts string with IP configuration into a list of IP addresses
        :param string: ip config in format {IP},{mask}[,gate][,dns]
        :return: tuple (IP, mask, gate, dns) or empty tuple
        """
        lower = string.lower()
        if not lower or lower == "dhcp" or lower == "none":  # invalid param
            return ()

        parts = string.split(SEP_IP)
        parts = [p for p in parts if p]  # remove empty strings

        if len(parts) == 2:
            return (parts[0], parts[1], parts[0], DNS_DEFAULT)
        elif len(parts) == 3:
            return tuple(parts + [DNS_DEFAULT])
        elif len(parts) == 4:
            return tuple(parts)
        else:
            raise ValueError


class Profile(object):
    """
    Class for storing wlan profile info
    """

    def __init__(self, ssid="", password="", bssid="", net=[]):
        self.ssid = ssid
        self.bssid = bssid
        self.password = password
        self.net = Net(net=net)

    @property
    def ssid(self):
        return self.__ssid

    @ssid.setter
    def ssid(self, val):
        if not val:  # check whether val is not empty
            raise ValueError
        self.__ssid = val

    @property
    def bssid(self):
        return self.__bssid

    @bssid.setter
    def bssid(self, val):
        if val and not Profile.isbssid(val):  # check correct BSSID(MAC) format
            raise ValueError
        self.__bssid = val

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, val):
        if val and len(val) < 8:  # min length of wifi password is 8, or 0 for no password
            raise ValueError
        self.__password = val

    @staticmethod
    def isbssid(mac):
        if not mac:
            return False
        mac = mac.upper()
        parts = mac.split(':')
        if len(parts) != 6:
            return False
        if any(not re.match("^[A-F0-9][A-F0-9]$", p) for p in parts):
            return False
        return True

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()

    def tolist(self):
        return [self.ssid, self.password, self.bssid, self.net.getnet()]

    def todict(self):
        return {"ssid": self.ssid, "password": self.password, "bssid": self.bssid, "net": self.net.getnet()}


class WLANconfig(object):
    """
    Class for storing wlan info
    """

    def __init__(self, enabled=False, profiles=[]):  # init default values
        self.enabled = enabled
        self.profiles = []
        for profile in profiles:
            self.profiles.append(Profile(**profile))

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()

    def tolist(self):
        return [self.enabled, self.profiles]

    def todict(self):
        return {"enabled": self.enabled, "profiles": [x.todict() for x in self.profiles]}


class ETHconfig(object):
    """
    Class for storing Ethernet info
    """

    def __init__(self, enabled=False, net=[]):  # init default values
        self.enabled = enabled
        self.net = Net(net=net)

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()

    def tolist(self):
        return [self.enabled, self.net.getnet()]

    def todict(self):
        return {"enabled": self.enabled, "net": self.net.getnet()}


class APconfig(object):
    """
    Class for storing hosted network info
    """

    def __init__(self, ssid="ReCo", password="12345678",
                 net=['192.168.0.1', '255.255.255.0', '192.168.0.1', '8.8.8.8']):  # init default values
        self.ssid = ssid
        self.password = password
        self.net = Net(net=net)

    @property
    def ssid(self):
        return self.__ssid

    @ssid.setter
    def ssid(self, val):
        if not val:  # check whether val is not empty
            raise ValueError
        self.__ssid = val

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, val):
        if len(val) < 8 and len(val) != 0:  # min length of wifi password is 8 or 0 for open network
            raise ValueError
        self.__password = val

    def tolist(self):
        return [self.ssid, self.password, self.net.getnet()]

    def todict(self):
        return {"ssid": self.ssid, "password": self.password, "net": self.net.getnet()}

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()


class Heosconfig(object):
    """
    Class for storing heos info
    """

    def __init__(self, name="", user="", password=""):
        self.name = name
        self.user = user
        self.password = password

    def tolist(self):
        return [self.name, self.user, self.password]

    def todict(self):
        return {"name": self.name, "user": self.user, "password": self.password}

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()


class Configuration(object):
    """
    Class for storing device configuration
    """

    def __init__(self, AP={}, ETH={}, WLAN={}, HEOS={}):
        self.AP = APconfig(**AP)
        self.ETH = ETHconfig(**ETH)
        self.WLAN = WLANconfig(**WLAN)
        self.HEOS = Heosconfig(**HEOS)

    def __str__(self):
        val = "AP:" + str(self.AP)
        val += "\nETH : " + str(self.ETH)
        val += "\nWLAN : " + str(self.WLAN)
        val += "\nHEOS : " + str(self.HEOS)
        return val

    def __repr__(self):
        return self.__str__()

    def todict(self):
        return {"AP": self.AP.todict(), "ETH": self.ETH.todict(), "WLAN": self.WLAN.todict(),
                "HEOS": self.HEOS.todict()}
