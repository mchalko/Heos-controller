import socket
import fileman

__serverSocket = None


class InvalidHeader(Exception):
    pass

__file_link = None
__file_heos = None
__config_link = fileman.Netconfig()
__config_heos = fileman.Heosconfig()

def start(linkfile, heosfile, port=80):
    """
    creates web server
    :param port: listen for http connection on this port
    """
    global __serverSocket
    global  __file_heos
    global  __file_link
    global  __config_heos
    global __config_link

    __file_link = linkfile
    __file_heos = heosfile
    __config_heos = fileman.load_heosconfig(__file_heos)
    __config_link = fileman.load_netconfig(__file_link)

    if not __config_heos or not __config_link: # invalid configs
        raise Exception

    if __serverSocket:  # close existing socket
        stop()

    __serverSocket = socket.socket()
    __serverSocket.bind(socket.getaddrinfo('0.0.0.0', port)[0][-1])
    __serverSocket.listen(1)
    __serverSocket.setblocking(False)  # do not actively wait

def stop():
    """
    stops the web server
    """
    global __serverSocket

    __serverSocket.close()
    __serverSocket = None


def __getHeader(line):
    header = line.strip()
    if not header:
        raise InvalidHeader
    parts = header.split(" ")

    if len(parts) != 3:
        raise InvalidHeader
    if parts[0] != "GET" and parts[0] != "POST":
        raise InvalidHeader
    if "HTTP" not in parts[2]:
        raise InvalidHeader

    return parts


def __handleRoot(socket):
    socket.senall("test123")


def listen():
    """
    call repeatedly to listen on port for connections and handle them
    """
    if not __serverSocket:
        return

    try:
        client, addr = __serverSocket.accept()  # throws OS error if no one is connected
        client.setblocking(False)

        try:
            method, path, version = __getHeader(client.readline())
            if method == "GET":
                if path == "/":  # send root web
                    __handleRoot(client)
                elif path == "/config":
                    client.sendall("succccces")
            elif method == "POST":
                if path == "/config":
                    client.sendall("POST succc")
        except InvalidHeader:
            pass  # ignore invalid or unsupported request

        client.close()
    except OSError:
        pass  # ignore
