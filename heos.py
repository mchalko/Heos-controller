import gc
import httputils
import time
import socket
import re

class Heos(object):
    pass


class DiscoveryService(object):
    SSDP_DISCOVERY = ["M-SEARCH * HTTP/1.1",
                      "HOST: 239.255.255.250:1900",
                      "MAN: \"ssdp:discover\"",
                      "MX: 4",
                      "ST: urn:schemas-denon-com:device:ACT-Denon:1",
                      "USER-AGENT: Esp32",
                      "\r\n"]
    SSDP_PORT = 1900
    SSDP_ADDR = "239.255.255.250"

    def __init__(self, interval):
        self.__interval = interval
        self.__onDiscover = []
        self.__socket = None
        self.__lastDiscover = 0

    def __sendDiscover(self):
        httputils.writesocket(self.__socket, '\r\n'.join(self.SSDP_DISCOVERY), self.SSDP_ADDR, self.SSDP_PORT)

    def start(self):
        if self.__socket is None:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create UDP socket
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind(('', self.SSDP_PORT))  # listen on ssdp port
            self.__socket.setblocking(False)  # do not actively wait
            mreq = bytes([int(x) for x in self.SSDP_ADDR.split(".")]) + bytes([0, 0, 0, 0])
            self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)  # join ssdp multicast group

    def stop(self):
        if self.__socket is not None:
            self.__socket.close()
        gc.collect()

    def discover(self):
        if not self.__socket:
            self.start()
            return

        if time.ticks_diff(time.ticks_ms(), self.__lastDiscover) > self.__interval:
            self.__lastDiscover = time.ticks_ms()
            self.__sendDiscover()

        try:
            data = self.__socket.recv(50)
            methodNotify = False
            if data and b"\r\n" in data:
                method, url, version = httputils.getrequest(data.decode("utf-8").split("\r\n")[0])
                methodNotify = method.upper() == "NOTIFY"

            while True:  # read the received message
                line = self.__socket.recv(500)
                if not line:
                    break
                if methodNotify:  # only interested in notify packets
                    data += line
            if methodNotify:
                lines = data.decode("utf-8").split("\r\n")
                for line in lines:
                    param, values = httputils.parseline(line)
                    ip = ""

                    if param.upper() == "LOCATION":
                        try:
                            ip = re.match("http://(.+):.*", values[0]).group(1)
                        except Exception:
                            pass

        except OSError:
            pass
        except httputils.InvalidHeader:
            pass

    def ondiscover(self, callback):
        """
        add on discover callback. If callback is None removes all existing callbacks
        :param callback: function that takes one param discovered ip - foo(ip)
        """
        if not callback:
            self.__onDiscover.clear()
        else:
            self.__onDiscover.append(callback)

    def __callondiscover(self):
        """
        call discovery callbacks
        """
        for callback in self.__onDiscover:
            callback()
