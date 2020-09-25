import socket
import fileman
import structures
import confweb
import netman
import gc
import select
import errno
import time
import machine

class InvalidHeader(Exception):
    pass


HTTP_CODES = {200: "OK",
              400: "Bad Request",
              404: "Not Found"}
DISOVER_INTERVAL_MS = 10000  # interval for rescanning wlan networks in reach

__serverSocket = None  # socket of webserver
# params of start() needed for saving the received configuration
__file = None
__config = None
# current wlans in reach
__available_wlans = []
__millis_wlandiscover = 0

__resetscheduled_ms = None # mark device reset call


def __respond(socket, data, code=200):
    """
    sends response with data to socket
    :param socket: client socket
    :param data: string to send
    :param code: response code
    """
    socket.send('HTTP/1.1 {} {}\n'.format(code, HTTP_CODES[code]))
    socket.send('Content-Type: text/html\n')
    socket.send('Connection: close\n\n')

    position = 0  # actual position in string
    datalen = len(data)  # total length  of data
    poll = select.poll()
    poll.register(socket, select.POLLOUT)  # register write poll

    while position < datalen:
        try:
            sent = socket.send(data[position:])  # sent & get number of bytes successfully sent
            position += sent
        except OSError as e:
            if e.args[0] == errno.ECONNRESET:  # connection aborted
                break
            poll.poll()  # wait until socket is writeable again

    poll.unregister(socket)


def __getHeader(line):
    if not line:  # blank line
        raise InvalidHeader

    header = line.strip().decode('utf-8')  # remove white chars and decode
    if not header:
        raise InvalidHeader

    parts = header.split(" ")
    if len(parts) != 3:  # http header always has 3 parts
        raise InvalidHeader
    if parts[0] != "GET" and parts[0] != "POST":  # other methods not supported
        raise InvalidHeader
    if "HTTP" not in parts[2]:
        raise InvalidHeader

    return parts


def __handleRoot(socket):
    __respond(socket, confweb.getWeb(__config, __available_wlans))


def __handleConfig(socket):
    data = b""
    while True:  # read the post data
        line = socket.readline()
        if not line:  # finish reading
            break
        data += line

    newconfig = structures.Configuration()
    data = data.decode('utf-8')
    parts = data.split("------")
    try:
        for p in parts:
            if not p:
                continue
            values = p.split("\r\n")
            values = values[1:]
            values = [v for v in values if v.strip()]
            if len(values) < 2:
                continue
            type = values[0].lower()
            value = values[1]
            if confweb.ATTR_AP_SSID in type:
                newconfig.AP.ssid = value
            elif confweb.ATTR_AP_PASS in type:
                newconfig.AP.password = value
            elif confweb.ATTR_AP_NET in type:
                newconfig.AP.net = fileman.Net(string=value)
            elif confweb.ATTR_ETH_NET in type:
                newconfig.ETH.net = fileman.Net(string=value)
            elif confweb.ATTR_ETH_EN in type:
                newconfig.ETH.enabled = value.lower() == "true"
            elif confweb.ATTR_WLAN_EN in type:
                newconfig.WLAN.enabled = value.lower() == "true"
            elif confweb.ATTR_WLAN_PROFILE in type:
                newconfig.WLAN.profiles.append(fileman.Profile(*value.split(fileman.SEP_VAL)))
            elif confweb.ATTR_HEOS_NAME in type:
                newconfig.HEOS.name = value
            elif confweb.ATTR_HEOS_USER in type:
                newconfig.HEOS.user = value
            elif confweb.ATTR_HEOS_PASS in type:
                newconfig.HEOS.password = value

        fileman.saveconfig(newconfig, __file)
        global __resetscheduled_ms
        __resetscheduled_ms = time.ticks_ms()
        __respond(socket, "Settings were successfully applied", 200)
    except ValueError:
        __respond(socket, "Settings are invalid", 400)


def start(configfile, port=80):
    """
    starts web server
    :param configfile: name of configuration file
    :param port: listen for http connection on this port
    """
    global __serverSocket
    global __file
    global __config

    __file = configfile
    __config = fileman.loadconfig(__file)

    if not __config:  # invalid config, use default to be able to connect
        __config = structures.Configuration()

    if __serverSocket:  # close existing socket
        stop()

    __serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    __serverSocket.bind(('', port))
    __serverSocket.listen(1)  # number of connections allowed
    __serverSocket.setblocking(False)  # do not actively wait


def stop():
    """
    stops the web server
    """
    global __serverSocket
    if __serverSocket:
        __serverSocket.close()
        __serverSocket = None
    gc.collect()


def listen():
    """
    call repeatedly to listen on port for connections and handle them
    """
    if not __serverSocket:
        return

    if __resetscheduled_ms is not None:
        if time.ticks_diff(time.ticks_ms(), __resetscheduled_ms) > 1000 : # ensure all connections are finished and closed
            __serverSocket.close()
            machine.reset()

    global __millis_wlandiscover
    global __available_wlans

    if time.ticks_diff(time.ticks_ms(), __millis_wlandiscover) > DISOVER_INTERVAL_MS:  # discover wlans
        __millis_wlandiscover = time.ticks_ms()
        __available_wlans = netman.discoverAPs()

    try:
        client, addr = __serverSocket.accept()  # throws OS error if no one is connected
        client.setblocking(False)

        try:
            firstline = client.readline()  # first line contains the important stuff
            while True:  # read the rest of the received http message
                line = client.readline()
                if not line or line == b"\r\n":
                    break

            method, path, version = __getHeader(firstline)
            if method == "GET":
                if path == "/":  # send root web
                    __handleRoot(client)
                else:  # invalid request
                    __respond(client, "Nothing is here", 404)
            elif method == "POST":
                if path == "/config":
                    __handleConfig(client)
                else:  # invalid request
                    __respond(client, "Nothing is here", 404)

        except InvalidHeader:
            pass  # ignore invalid or unsupported request
        except Exception as e:
            raise e
        finally:
            client.close()  # close the client socket
    except OSError:
        pass  # ignore


