import network
import machine
import configfile as attr
import ubinascii

AUTHMODE = {network.AUTH_OPEN: "open",
            network.AUTH_WEP: "WEP",
            network.AUTH_WPA_PSK: "WPA-PSK",
            network.AUTH_WPA2_PSK: "WPA2-PSK",
            network.AUTH_WPA_WPA2_PSK: "WPA/WPA2-PSK"}

__interface_AP = network.WLAN(network.AP_IF)
__interface_STA = network.WLAN(network.STA_IF)
__interface_ETH = network.LAN(mdc=machine.Pin(13), mdio=machine.Pin(14), power=machine.Pin(32), id=None, phy_addr=0,
                              phy_type=network.PHY_LAN8720)

__ETH_en = False
__ETH_conf = None
__WLAN_en = False
__WLAN_conf = None
__WLAN_profiles = {}


def __connectETH(ifconfig=None):
    if ifconfig:  # use static ip
        __interface_ETH.ifconfig(ifconfig)
    else:  # use dhcp
        __interface_ETH.ifconfig()
    __interface_ETH.active(True)


def __connectWLAN(ssid, password, ifconfig=None):
    if ifconfig:
        __interface_STA.ifconfig(ifconfig)
    __interface_STA.active(True)
    __interface_STA.connect(ssid, password)


def connect(config):
    """
    parses configuration from file and tries to connect to a network
    :param config: configuration file
    :return: True on successful configuration, connecting was initiated
    """

    global __ETH_en
    global __ETH_conf
    global __WLAN_en
    global __WLAN_conf
    global __WLAN_profiles

    try:
        with open(config) as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()  # remove ending and trailing white spaces
                if not len(line) or line[0] == '#':  # skip lines starting with '#'
                    continue
                # parse file
                parts = line.split(attr.ATTR_SPLIT_CHAR)
                if parts[0].upper() == attr.ATTR_WLAN:
                    if parts[1].upper() == attr.ATTR_CONF:
                        __WLAN_conf = tuple(parts[2].split(attr.VAL_SPLIT_CHAR))
                    if parts[1].upper() == attr.ATTR_ENABLE:
                        __WLAN_en = parts[2].lower() == "true"
                    if parts[1].upper() == attr.ATTR_PROFILE:
                        profile = parts[2].split(attr.VAL_SPLIT_CHAR)
                        __WLAN_profiles[profile[0]] = profile[1] if len(profile) == 2 else None
                elif parts[0].upper() == attr.ATTR_LAN:
                    if parts[1].upper() == attr.ATTR_CONF:
                        __ETH_conf = tuple(parts[2].split(attr.VAL_SPLIT_CHAR))
                    elif parts[1].upper() == attr.ATTR_ENABLE:
                        __ETH_en = parts[2].lower() == "true"

            reconnect()
            return __ETH_en or __WLAN_en
    except OSError:
        return False


def reconnect():
    """
    tries to connect to a network using existing configuration (previously used in connect())
    """
    if __ETH_en:
        __connectETH(__ETH_conf)
    if __WLAN_en:
        networks = discoverAPs()
        for ssid, _ in networks:  # check if networks are available
            if ssid in __WLAN_profiles:
                __connectWLAN(ssid, __WLAN_profiles[ssid], __WLAN_conf)


def disconnect():
    if __ETH_en:
        __interface_ETH.active(False)
    if __WLAN_en:
        __interface_STA.disconnect()
        __interface_STA.active(False)


def status():
    """
    get status of interfaces
    :return: tuple of statuses: (WLAN status, Ethernet status)
    """
    return (__interface_STA.status(), __interface_ETH.status())


def isconnected():
    """

    :return: True if connection was initiated at least on one interface
    """
    return __interface_STA.isconnected() or __interface_ETH.isconnected()


def activateAP(ssid, password):
    """
    creates an access point with WPA2 security.
    module address is 192.168.0.1
    :param ssid: ssid of network
    :param password: password of network
    """
    __interface_AP.ifconfig(("192.168.0.1", "255.255.255.0", "192.168.0.1", "192.168.0.1"))
    __interface_AP.active(True)
    __interface_AP.config(essid=ssid, password=password, authmode=network.AUTH_WPA2_PSK)


def deactivateAP():
    """
    disables the access point
    """
    __interface_AP.active(False)


def discoverAPs():
    """
    :return: list of lists of access points in range [ssid, mac, RSSI, authmode]
    """
    __interface_STA.active(True)
    networks = __interface_STA.scan()
    netlist = []  # final list of networks
    for n in networks:
        netlist.append([n[0].decode('utf-8'),
                        ubinascii.hexlify(n[1], ':').decode('ascii').upper(),
                        str(n[3])+"dBm",
                        AUTHMODE[n[4]]])
    return netlist
