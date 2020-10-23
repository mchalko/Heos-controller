import network
import machine
import ubinascii

AUTHMODE = {network.AUTH_OPEN: "open",
            network.AUTH_WEP: "WEP",
            network.AUTH_WPA_PSK: "WPA-PSK",
            network.AUTH_WPA2_PSK: "WPA2-PSK",
            network.AUTH_WPA_WPA2_PSK: "WPA/WPA2-PSK"}

__interface_AP = network.WLAN(network.AP_IF)
__interface_STA = network.WLAN(network.STA_IF)
__interface_ETH = network.LAN(mdc=machine.Pin(13), mdio=machine.Pin(14), power=machine.Pin(32), phy_addr=0,
                              phy_type=network.PHY_LAN8720)


def connectETH(ifconfig=None):
    """
    initiates connecting to lan network
    once static address is set, if config can't be switched back to dhcp (library bug)
    :param ifconfig: tuple with ip config addresses - strings (IP, mask, gate, dns) or None for dhcp
    """
    print("Connecting to Ethernet")
    if ifconfig:  # use static ip
        __interface_ETH.ifconfig(ifconfig)

    __interface_ETH.active(True)


def connectWLAN(ssid, password, ifconfig=None, bssid=None):
    """
    connects to wifi network
    once static address is set, ip config can't be switched back to dhcp (library bug)
    :param ssid: ssid
    :param password: password
    :param ifconfig: tuple with ip config addresses - strings (IP, mask, gate, dns) or None for dhcp
    :param bssid: mac of network
    """
    print("Connecting to wifi : ", ssid, password, ifconfig, bssid)
    if ifconfig:  # use static ip
        __interface_STA.ifconfig(ifconfig)
    __interface_STA.active(True)
    # empty pass string means no password. SSID can't be empty
    if not ssid:
        return
    __interface_STA.connect(ssid, password if password else None, bssid=ubinascii.unhexlify(bssid.replace(":", "")) if bssid else None)


def connect(wlanconfig=None, ethconfig=None):
    """
    tries to connect to a network
    :param wlanconfig: WLANconfig object
    :param ethconfig: ETHconfig object
    :return: True if connection was initiated
    """

    if ethconfig and ethconfig.enabled:
        connectETH(ethconfig.net.getnet())
    if wlanconfig and wlanconfig.enabled:
        networks = discoverAPs()
        for ssid, bssid, rssi, auth, hidden in networks:  # loop through available networks
            for profile in wlanconfig.profiles:  # check each known network
                if profile.ssid == ssid:  # ssid match
                    if not profile.bssid:  # bssid isn't specified in network profile, connect
                        connectWLAN(profile.ssid, profile.password, profile.net.getnet())
                        return True
                    elif profile.bssid == bssid:  # check if bssid matches
                        connectWLAN(profile.ssid, profile.password, profile.net.getnet(), profile.bssid)
                        return True

    return (wlanconfig and wlanconfig.enabled) or (ethconfig and ethconfig.enabled)


def disconnect():
    """
    deactivates eth and wlan network connections
    """
    if __interface_ETH.active():
        __interface_ETH.active(False)
    if __interface_STA.active():
        if __interface_STA.isconnected():
            __interface_STA.disconnect()
        __interface_STA.active(False)


def status():
    """
    get status of interfaces
    :return: tuple of statuses: (WLAN status, Ethernet status, AP status)
    """
    return (__interface_STA.status(), __interface_ETH.status(), __interface_AP.status())


def statusWLAN():
    return __interface_STA.status()


def statusAP():
    return __interface_AP.status()


def statusETH():
    return __interface_ETH.status()


def addrAP():
    return __interface_AP.ifconfig()


def addrWLAN():
    return __interface_STA.ifconfig()


def addrETH():
    return __interface_ETH.ifconfig()

def isconnectingETH():
    return statusETH() == network.STAT_CONNECTING

def isconnectingWLAN():
    return statusWLAN() == network.STAT_CONNECTING

def isconnected():
    """

    :return: True if connection was initiated at least on one interface
    """
    return __interface_STA.isconnected() or __interface_ETH.isconnected()


def startAP(apconfig):
    """
    creates an access point using given params
    :param apconfig: APconfig object
    """
    print("Starting access point")
    net = apconfig.net.getnet()
    if net:
        __interface_AP.ifconfig(net)
    __interface_AP.active(True)
    __interface_AP.config(essid=apconfig.ssid, password=apconfig.password,
                          authmode=network.AUTH_OPEN if not apconfig.password else network.AUTH_WPA2_PSK)


def stopAP():
    """
    disables the access point
    """
    __interface_AP.active(False)


def discoverAPs():
    """
    :return: list of lists of access points in range [ssid, bssid, RSSI, authmode, hidden]
    """
    __interface_STA.active(True)
    networks = __interface_STA.scan()
    netlist = []  # final list of networks
    for n in networks:
        netlist.append([n[0].decode('utf-8'),
                        ubinascii.hexlify(n[1], ':').decode('ascii').upper(),
                        str(n[3]) + " dBm",
                        AUTHMODE[n[4]],
                        str(n[5]).lower()])
    return netlist
