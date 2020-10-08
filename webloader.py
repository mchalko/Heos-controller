FOLDER_WEB = "/www"
FILE_WEB_ROOT = "/index.html"
FILE_WEB_UPDATE = "/update.html"

ATTR_AP_SSID = "ap_ssid"
ATTR_AP_PASS = "ap_pass"
ATTR_AP_NET = "ap_net"
ATTR_ETH_EN = "eth_en"
ATTR_ETH_NET = "eth_net"
ATTR_WLAN_EN = "wlan_en"
ATTR_WLAN_PROFILE = "wlan_profile"
ATTR_HEOS_NAME = "heos_name"
ATTR_HEOS_USER = "heos_user"
ATTR_HEOS_PASS = "heos_pass"

CUSTOM_DATA_BEGIN = ""
CUSTOM_DATA_END = ""


def getrootvars(conf, networks):
    """
    :param conf: device config
    :param networks: available networks
    :return: variables for root web
    """
    result = 'var ap_ssid="{}";'.format(conf.AP.ssid)
    result += 'var ap_pass="{}";'.format(conf.AP.password)
    net = conf.AP.net.getnet()
    result += 'var ap_net={};'.format(list(net[:2]) if net else "\"\"")
    result += 'var eth_en={};'.format(str(conf.ETH.enabled).lower())
    net = conf.ETH.net.getnet()
    result += 'var eth_net={};'.format(list(net[:3]) if net else "\"\"")
    result += 'var wlan_en={};'.format(str(conf.WLAN.enabled).lower())
    result += 'var heos_name="{}";'.format(conf.HEOS.name)
    result += 'var heos_user="{}";'.format(conf.HEOS.user)
    result += 'var heos_pass="{}";'.format(conf.HEOS.password)
    result += 'var ssids={};'.format(networks)
    result += 'var knownNetworks={};'.format(str(conf.WLAN.profiles))
    return result


def root(conf, networks):
    data = ""
    with open(FOLDER_WEB + FILE_WEB_ROOT) as file:
        skipLines = False
        while True:
            line = file.readline()
            stripped = line.strip()
            if stripped == CUSTOM_DATA_BEGIN:
                skipLines = True
                data += getrootvars(conf, networks)
            elif stripped == CUSTOM_DATA_END:
                skipLines = False
                continue
            if not skipLines:
                data += line
    return data


def update():
    data = ""
    with open(FOLDER_WEB + FILE_WEB_UPDATE) as file:
        data += file.read()
    return data
