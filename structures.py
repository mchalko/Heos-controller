import re

DNS_DEFAULT = "8.8.8.8"
SEP_IP = ","


class Net(object):
    """
    class for storing ip configuration of a network
    """

    def __init__(self, string="", net=[]):
        if len(net):
            self.__conf = Net.nettostring(*net)
        else:

            self.__conf = "" if string.lower() == "none" else string

        net = Net.stringtonet(self.__conf)
          # contains ip tuples
        if net and any(not Net.isip(ip) for ip in net):
            raise ValueError  # raise error if invalid ip detected

    def getstring(self):
        return self.__conf

    def getnet(self):
        return Net.stringtonet(self.__conf)

    def __repr__(self):
        return self.__conf

    def __str__(self):
        return self.__conf

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
    def nettostring(ip=None, mask=None, gate=None, dns=None):
        """
        Converts ip configuration - list of ip addresses into string
        """
        val = ""
        if ip:
            val = ip + SEP_IP + mask
            if gate:
                val += SEP_IP + gate
            if dns:
                val += SEP_IP + dns
        return val

    @staticmethod
    def stringtonet(string):
        """
        Converts string with IP configuration into a list of IP addresses
        :param string: ip config in format {IP},{mask}[,gate][,dns]
        :return: tuple (IP, mask, gate, dns) or empty string
        """
        if string=="" or string.lower() == "dhcp":  # invalid param
            return ""

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

    def __init__(self, ssid="", password="", bssid="", net=""):
        self.ssid = ssid
        self.bssid = bssid
        self.password = password
        self.net = Net(string=net)


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
        return [self.ssid, self.password, self.bssid, self.net.getstring()]


class WLANconfig(object):
    """
    Class for storing wlan info
    """

    def __init__(self):  # init default values
        self.enabled = False
        self.profiles = []

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()

    def tolist(self):
        return [self.enabled, self.profiles]


class ETHconfig(object):
    """
    Class for storing Ethernet info
    """

    def __init__(self):  # init default values
        self.enabled = False
        self.net = Net()

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()

    def tolist(self):
        return [self.enabled, self.net.getstring()]


class APconfig(object):
    """
    Class for storing hosted network info
    """

    def __init__(self):  # init default values
        self.ssid = "ReCo"
        self.password = "12345678"
        self.net = Net(string="192.168.0.1,255.255.255.0")

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
        if len(val) < 8:  # min length of wifi password is 8
            raise ValueError
        self.__password = val

    def tolist(self):
        return [self.ssid, self.password, self.net.getstring()]

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

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return self.__str__()


class Configuration(object):
    """
    Class for storing device configuration
    """

    def __init__(self):
        self.AP = APconfig()
        self.ETH = ETHconfig()
        self.WLAN = WLANconfig()
        self.HEOS = Heosconfig()

    def __str__(self):
        val = "AP:" + str(self.AP)
        val += "\nETH : " + str(self.ETH)
        val += "\nWLAN : " + str(self.WLAN)
        val += "\nHEOS : " + str(self.HEOS)
        return val

    def __repr__(self):
        return self.__str__()

