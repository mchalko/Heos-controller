import network
import machine
import fileman as conf
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

def __connectETH(ifconfig=None):
    config = conf.stringtoip(ifconfig)
    if config:  # use static ip
        __interface_ETH.ifconfig(config)
    else:  # use dhcp
        __interface_ETH.ifconfig()
    __interface_ETH.active(True)


def __connectWLAN(ssid, password, ifconfig=None, bssid=None):
    config = conf.stringtoip(ifconfig)
    if config:
        __interface_STA.ifconfig(config)
    __interface_STA.active(True)

    __interface_STA.connect(ssid, password, bssid=bssid)

def connect(config):
    """
    tries to connect to a network
    :param config: configuration of the connection
    :return: True if connecting was initiated
    """

    if config.ETH_en:
        __connectETH(config.ETH_conf)
    if config.WLAN_en:
        networks = discoverAPs()
        for ssid, bssid, _ in networks:  # check if networks are available
            for profile in config.WLAN_profiles:
                if profile.ssid == ssid:
                    if not profile.bssid :
                        __connectWLAN(profile.ssid, profile.password, profile.conf)
                        return True
                    elif profile.bssid == bssid:
                        __connectWLAN(profile.ssid, profile.password, profile.conf, profile.bssid)
                        return True
    return __configuration.ETH_en or __configuration.WLAN_en


def disconnect():
    __interface_ETH.active(False)
    if __interface_STA.isconnected():
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


def activateAP(config):
    """
    creates an access point using given configuration with WPA2 security.
    :param config: configuration
    """
    __interface_AP.ifconfig(config.AP_conf)
    __interface_AP.active(True)
    __interface_AP.config(essid=config.AP_ssid, password=config.AP_pass, authmode=network.AUTH_WPA2_PSK)


def deactivateAP():
    """
    disables the access point
    """
    __interface_AP.active(False)


def discoverAPs():
    """
    :return: list of lists of access points in range [ssid, bssid, RSSI, authmode]
    """
    __interface_STA.active(True)
    networks = __interface_STA.scan()
    netlist = []  # final list of networks
    for n in networks:
        netlist.append([n[0].decode('utf-8'),
                        ubinascii.hexlify(n[1], ':').decode('ascii').upper(),
                        str(n[3])+" dBm",
                        AUTHMODE[n[4]]])
    return netlist
