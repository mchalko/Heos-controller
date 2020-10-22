import gc
import httputils
import time
import socket
import re
import json
import structures


class Heos(object):
    COMMAND_HEARTHBEAT = ("system/heart_beat", {})
    COMMAND_LOGIN = ("system/sign_in", {"un": "", "pw": ""})
    COMMAND_GETPLAYERS = ("player/get_players", {})
    COMMAND_GETSTATE = ("player/get_play_state", {"pid": ""})

    HEOS_PORT = 1255
    # private default callbacks
    __CMD_CONNECTED_CB = "_connect"
    __CMD_DISCONNECTED_CB = "_disconnect"
    # connection types
    CONNECTION_NOT_CONNECTED = 0
    CONNECTION_CONNECTING = 1
    CONNECTION_CONNECTED = 2

    def __init__(self, config, interval=4000):
        """
        :param config: Heosconfig containing user, password and heos name
        :param interval: interval for periodic sending of commands
        """
        self.__config = config
        self.__interval = interval
        self.__timeout = interval * 3 # after timeout heos is considered dead
        self.__callbacks = {}
        self.__socket = None

        self.__lastHearthbeat = 0
        self.__lastCmdRecieved = 0
        self.__lastGetstate = 0
        self.__lastSign = 0
        self.__lastGetplayers = 0

        self.__connection = Heos.CONNECTION_NOT_CONNECTED
        self.__pid = ""
        self.__status = ""
        self.__signed = False

    def __encode(self, string):
        """
        encodes heos param string to be compliant with the format
        :param string: string to encode
        """
        return string.replace("%", "%25").replace("&", "%26").replace("=", "%3D")

    def __callCallback(self, command, param=None):
        """
        calls callback from dictionary based on command
        :param command: command for callback
        :param param: optional parameter fro callback
        """
        if command in self.__callbacks:
            for callback in self.__callbacks[command]:
                if param:
                    callback(param)
                else:
                    callback()

    def start(self, ip):
        """
        initialize communication with the device
        """
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create TCP socket
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse address, to prevent errors on reboot
            self.__socket.connect((ip, self.HEOS_PORT))  # listen on heos telnet port for responses
            self.__socket.setblocking(False)  # do not actively wait
            self.__connection = Heos.CONNECTION_CONNECTING
            self.__lastCmdRecieved = time.ticks_ms()  # set start time

    def stop(self):
        """
        stop communication with the device & cleanup
        """
        if self.__socket is not None:
            self.__socket.close()
            self.__socket = None
        gc.collect()

    def run(self):
        """
        run baseline communication with heos device
        should be called in loop
        """
        if not self.__socket: # if not started do nothing
            return

        try:
            data = self.__socket.recv(2048) # recieve max 2kB of data from socket (if bigger other data are lost)
            if data:
                datajson = json.loads(data)
                command = datajson["heos"]["command"]
                result = datajson["heos"]["result"] == "success"
                if result:
                    self.__lastCmdRecieved = time.ticks_ms()
                    if command == self.COMMAND_HEARTHBEAT[0]:
                        if not self.__isconnected:  # first connection successful
                            self.__connection = Heos.CONNECTION_CONNECTED
                            self.__callCallback(self.__CMD_CONNECTED_CB)
                    elif command == self.COMMAND_GETPLAYERS[0]:
                        for item in datajson["payload"]:
                            if item["name"] == self.__config.name:
                                self.__pid = item["pid"]
                    elif command == self.COMMAND_LOGIN[0]:
                        self.__signed = True
                    elif command == self.COMMAND_GETSTATE[0]:
                        self.__status = data["heos"]["message"].split("state=", 1)[1]
                if command in self.__callbacks:
                    self.__callCallback(command, datajson)
        except OSError: # do nothing if socket can't be read
            pass

        if time.ticks_diff(time.ticks_ms(), self.__lastCmdRecieved) > self.__timeout:  # watch out for timeout
            self.__lastCmdRecieved = time.ticks_ms()
            self.__connection = Heos.CONNECTION_NOT_CONNECTED
            self.__signed = False
            self.__status = ""
            self.__pid = ""
            self.__callCallback(self.__CMD_DISCONNECTED_CB)

        if time.ticks_diff(time.ticks_ms(), self.__lastHearthbeat) > self.__interval:  # send hearth beat
            self.__lastHearthbeat = time.ticks_ms()
            self.send(*self.COMMAND_HEARTHBEAT)

        if self.isconnected() and not self.issigned():
            if time.ticks_diff(time.ticks_ms(), self.__lastSign) > self.__interval:  # try signing in
                self.__lastSign = time.ticks_ms()
                self.send(*Heos.formatcmd(self.COMMAND_LOGIN, un=self.__config.user, pw=self.__config.password))

        if self.issigned() and not self.getpid():
            if time.ticks_diff(time.ticks_ms(), self.__lastGetplayers) > self.__interval:  # retrieve device info
                self.__lastGetplayers = time.ticks_ms()
                self.send(*self.COMMAND_GETPLAYERS)

        if self.issigned() and self.getpid():  # device is fully functioning
            if time.ticks_diff(time.ticks_ms(), self.__lastGetstate) > self.__interval:  # get player state
                self.__lastGetstate = time.ticks_ms()
                self.send(*Heos.formatcmd(self.COMMAND_GETSTATE, pid=self.__pid))

    def send(self, command, attributes={}):
        """
        Sends a command to heos device
        :param command: command for device
        :param attributes: attributes of given command
        """
        if self.__socket:
            if attributes:
                attribs = "&".join(["{}={}".format(self.__encode(k), self.__encode(v)) for k, v in attributes.items()])
                request = "heos://{}?{}\r\n".format(command, attribs)
            else:
                request = "heos://{}\r\n".format(command)
            httputils.writesocket(self.__socket, request)

    @staticmethod
    def formatcmd(command, **kwargs):
        """
        formats heos command - adds attributes
        :param command: heos command
        :param kwargs: attributes
        :return complete command
        """
        for k, v in kwargs.items():
            if k in command[1]:
                command[k] = v
        return command

    def getconnection(self):
        """
        :return: heos connection status
        """
        return self.__connection

    def getstatus(self):
        """
        :return: status of selected (by config) heos player
        """
        return self.__status

    def issigned(self):
        """
        :return: sign in was successful on selected (by config) heos player
        """
        return self.__signed

    def getpid(self):
        """
        :return: pid (player id) of selected (by config) heos player
        """
        return self.__pid

    def ondisconnect(self, callback):
        """
        Callback for loss of connection with heos device
        When callback is None removes all callbacks
        :param callback: function without parameters - foo()
        """
        self.oncommand(self.__CMD_DISCONNECTED_CB, callback)

    def onconnect(self, callback):
        """
        Callback called on successful connection to heos device
        When callback is None removes all callbacks
        :param callback: function without parameters - foo()
        """
        self.oncommand(self.__CMD_CONNECTED_CB, callback)

    def oncommand(self, command, callback):
        """
        add callback for recieved commands. Callback will be invoked if heos sends response for given command
        :param command: command for which callback will be invoked (eg system/reboot)
        :param callback:
        :return:
        """
        if command in self.__callbacks:
            if callback:
                self.__callbacks[command].append(callback)
            else:
                self.__callbacks[command].clear()
        elif callback:
            self.__callbacks[command] = [callback]


class DiscoveryService(object):
    # names of heos
    DEVICE_NAME = ["urn:schemas-denon-com:device:ACT-Denon:1", "urn:schemas-denon-com:device:AiosDevice:1"]
    SSDP_DISCOVERY = ["M-SEARCH * HTTP/1.1",
                      "HOST: 239.255.255.250:1900",
                      "MAN: \"ssdp:discover\"",
                      "MX: 4",
                      "ST: urn:schemas-denon-com:device:ACT-Denon:1",
                      "USER-AGENT: Esp32",
                      "\r\n"]
    SSDP_PORT = 1900
    SSDP_ADDR = "239.255.255.250"

    def __init__(self, interval=5000):
        """
        Creates a discovery service object
        :param interval: interval in ms for sending discovery requests
        """
        self.__interval = interval

        self.__onDiscover = []
        self.__socket = None
        self.__lastDiscover = 0

    def __sendDiscover(self):
        """
        sends discover packet
        """
        httputils.writesocket(self.__socket, '\r\n'.join(self.SSDP_DISCOVERY), self.SSDP_ADDR, self.SSDP_PORT)

    def start(self):
        """
        start & init discovery
        """
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create UDP socket
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind(('', self.SSDP_PORT))  # listen on ssdp port
            self.__socket.setblocking(False)  # do not actively wait
            mreq = bytes([int(x) for x in self.SSDP_ADDR.split(".")]) + bytes([0, 0, 0, 0])
            self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)  # join ssdp multicast group

    def stop(self):
        """
        stop discovery & cleanup
        """
        if self.__socket is not None:
            self.__socket.close()
            self.__socket = None
        gc.collect()

    def discover(self):
        """
         run device discovery
         should be called in a loop
        """
        if not self.__socket:
            self.start() # start automatically
            return

        if time.ticks_diff(time.ticks_ms(), self.__lastDiscover) > self.__interval: # send discover
            self.__lastDiscover = time.ticks_ms()
            self.__sendDiscover()

        try:
            data = self.__socket.recv(512) # get only 512B of data from socket
            if not data:
                return

            lines = data.decode("utf-8").split("\r\n")

            headerparts = lines[0].lower().split(" ") # first line contains header
            if len(headerparts) != 3 or (headerparts[0] != "notify" and headerparts[1] != "200"):
                return # invalid header reciever - ignore

            ip = ""
            valid = False

            for line in lines:
                param, values = httputils.parseline(line)
                if param == "location": # get ip address
                    try:
                        ip = re.match("http://(.+):.*", values[0]).group(1)
                    except Exception:  # catch exception on invalid match
                        pass
                elif param == "nt" or param == "st":
                    if any(d in values for d in self.DEVICE_NAME):
                        valid = True # device found

            if ip and valid:
                self.__callondiscover(ip)
        except OSError: # do nothing if socket is empty
            pass

    def ondiscover(self, callback):
        """
        add on discover callback. If callback is None removes all existing callbacks
        :param callback: function that takes one param discovered ip - foo("ip")
        """
        if not callback:
            self.__onDiscover.clear()
        else:
            self.__onDiscover.append(callback)

    def __callondiscover(self, ip):
        """
        call discovery callbacks
        """
        for callback in self.__onDiscover:
            callback(ip)
