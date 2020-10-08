import socket
import gc
import time
import machine

import config
import structures
import netconnect
import httputils
from requesthandler import *

__serverSocket = None  # socket of webserver
# current wlans in reach
__available_wlans = []
__millis_wlandiscover = 0
DISOVER_INTERVAL_MS = 10000  # interval for rescanning wlan networks in reach

__resetscheduled_ms = None  # mark device reset call


def schedulereboot():
    global __resetscheduled_ms
    __resetscheduled_ms = time.ticks_ms()


def start(configfile, port=80):
    """
    starts web server
    :param configfile: name of configuration file
    :param port: listen for http connection on this port
    """
    global __serverSocket

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
    # check whether reboot is pending
    if __resetscheduled_ms is not None:
        if time.ticks_diff(time.ticks_ms(),
                           __resetscheduled_ms) > 1000:  # ensure all connections are finished and closed
            __serverSocket.close()
            machine.reset()

    # periodically discover wlans
    global __millis_wlandiscover
    global __available_wlans
    if time.ticks_diff(time.ticks_ms(), __millis_wlandiscover) > DISOVER_INTERVAL_MS:  # discover wlans
        __millis_wlandiscover = time.ticks_ms()
        __available_wlans = netconnect.discoverAPs()

    # handle client request
    try:
        client, addr = __serverSocket.accept()  # throws OS error if no one is connected
        client.setblocking(False)

        try:
            boundary = ""
            method, path, version = httputils.getrequest(client.readline())  # first line contains the important stuff
            while True:  # read the rest of the received http message
                line = client.readline()
                if not line or line == b"\r\n":
                    break
                if method == "POST":  # try to get form boundary from post method
                    param, values = httputils.parseline(line)
                    if param == "content-type":
                        if values[0].lower() == "multipart/form-data" and len(values) > 1:
                            boundary = values[1].replace("boundary=", "")

            if method == "GET":
                if path == "/":  # send root web
                    get_root(client)
                elif path == "/update":
                    get_update(client)
                else:  # invalid request
                    httputils.response(client, "Nothing is here", 404)
            elif method == "POST":
                if path == "/update/submit":
                    post_update_submit(client, boundary)
                elif path == "/get/wlans":
                    post_get_wlans(client, __available_wlans)
                elif path == "/get/config":
                    post_get_config(client)
                elif path == "/set/config":
                    post_set_config(client)
                elif path == "/add/network":
                    post_add_network(client)
                elif path == "/remove/network":
                    post_remove_network(client)
                elif path == "/reboot":
                    post_reboot(client)
                    schedulereboot()
                else:  # invalid request
                    httputils.response(client, code=404)

        except httputils.InvalidHeader:
            pass  # ignore invalid or unsupported request
        except Exception as e:  # except anything to make sure that socket will be closed
            raise e
        finally:
            client.close()  # close the client socket
    except OSError:
        pass  # ignore
