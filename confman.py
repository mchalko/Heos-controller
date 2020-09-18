import socket

__serverSocket = None


class InvalidHeader(Exception):
    pass


def start(port=80):
    """
    creates web server
    :param port: listen for http connection on this port
    """
    global __serverSocket

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


def __handleRoot():
    pass


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
            header = __getHeader(client.readline())
            if header[0] == "GET":
                if header[1] == "/":  # send root web
                    pass
            elif header[0] == "POST":
                pass
        except InvalidHeader:
            pass  # ignore invalid or unsupported request

        client.close()
    except OSError:
        pass  # ignore
