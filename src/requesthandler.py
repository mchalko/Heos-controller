import httputils
import structures
import config
import json
import os
from led import Led
import led
from boot import FILE_UPDATE, FOLDER_UPDATE

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

FOLDER_WEB = "/www/"
FILE_WEB_ROOT = FOLDER_WEB + "index.html"
FILE_WEB_UPDATE = FOLDER_WEB + "update.html"

leds = (Led(2), Led(23), Led(5), Led(4), Led(18), Led(17))

def get_root(socket):
    httputils.sendfromfile(socket, FILE_WEB_ROOT)


def get_update(socket):
    httputils.sendfromfile(socket, FILE_WEB_UPDATE)


def post_get_wlans(socket, wlans):
    httputils.response(socket, json.dumps(wlans), type=httputils.TYPE_JSON)


def post_get_config(socket):
    httputils.response(socket, json.dumps(config.loadconfig().todict()), type=httputils.TYPE_JSON)


def post_reboot(socket):
    httputils.response(socket, "Rebooting")


def post_set_config(socket):
    conf = config.loadconfig()
    try:
        while True:  # read the post data
            line = socket.readline(512)
            if not line:  # finish reading
                break
            param, values = httputils.parseline(line.decode("utf-8"))
            if param == "content-disposition":
                type = values[1].lower()
                socket.readline()  # consume blank line
                value = socket.readline().decode('utf-8')[:-2]  # get value, remove "\r\n"

                if ATTR_AP_SSID in type:
                    conf.AP.ssid = value
                elif ATTR_AP_PASS in type:
                    conf.AP.password = value
                elif ATTR_AP_NET in type:
                    conf.AP.net = config.Net(string=value)
                elif ATTR_ETH_NET in type:
                    conf.ETH.net = config.Net(string=value)
                elif ATTR_ETH_EN in type:
                    conf.ETH.enabled = value.lower() == "true"
                elif ATTR_WLAN_EN in type:
                    conf.WLAN.enabled = value.lower() == "true"
                elif ATTR_HEOS_NAME in type:
                    conf.HEOS.name = value
                elif ATTR_HEOS_USER in type:
                    conf.HEOS.user = value
                elif ATTR_HEOS_PASS in type:
                    conf.HEOS.password = value

        config.saveconfig(conf)
        httputils.response(socket, "Settings were successfully applied", 200)
    except ValueError:
        httputils.response(socket, "Settings are invalid", 400)


def post_add_network(socket):
    conf = config.loadconfig()
    try:
        conf.WLAN.profiles.append(structures.Profile(**json.load(socket)))
        config.saveconfig(conf)
        httputils.response(socket)
    except Exception:
        httputils.response(socket, code=400)


def post_remove_network(socket):
    conf = config.loadconfig()
    try:
        toDelete = json.load(socket)
        for i, profile in enumerate(conf.WLAN.profiles):
            if profile.ssid == toDelete["ssid"]:
                if not toDelete["bssid"] or toDelete["bssid"] == profile.bssid:
                    del conf.WLAN.profiles[i]
        config.saveconfig(conf)
        httputils.response(socket)
    except Exception:
        httputils.response(socket, code=400)


def post_update_submit(socket, boundary):
    fileWritten = False  # something received
    inFile = False  # reading file
    toWrite = None  # buffer for line to write
    try:
        os.mkdir(FOLDER_UPDATE.rstrip('/'))
    except OSError:
        pass
    file = open(FILE_UPDATE, "wb")  # create, open file for storing update
    while True:  # read the post data
        line = socket.readline(1024)
        if not line:  # finish reading
            break
        led.blink_connecting(*leds)
        try:
            if boundary in line.decode("utf-8"):
                inFile = False
                if toWrite:  # write the last line, omit last 2 chars (\r\n)
                    fileWritten = True
                    file.write(toWrite[:-2])
                toWrite = None
                continue
        except UnicodeError:  # throws error if in file
            pass

        if toWrite:  # something is in buffer
            file.write(toWrite)

        if inFile:
            toWrite = line  # set to write in the next cycle
            continue

        param, values = httputils.parseline(line.decode("utf-8"))
        if param == "content-disposition" and any("filename" in val for val in values):
            while True:
                line = socket.readline()
                if line == b"\r\n":
                    break
            inFile = True
    file.close()
    httputils.response(socket)
    for l in leds:
        l.off()
    return fileWritten


