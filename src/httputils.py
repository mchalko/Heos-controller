import select
import errno

HTTP_CODES = {200: "OK",
              400: "Bad Request",
              404: "Not Found"}
TYPE_JSON = "application/json"
TYPE_HTML = "text/html"


class InvalidHeader(Exception):
    pass


def sendfromfile(socket, file):
    """
    sends web page read from file into a socket
    :param socket: client socket
    :param file: file name
    """
    with open(file, "r") as f:
        response(socket, "")  # send response header
        while True:
            try:
                chunk = f.read(512)
            except OSError:
                break
            if not chunk:
                break
            writesocket(socket, chunk)  # send file content


def response(socket, data="", code=200, type=TYPE_HTML):
    """
    sends response with optional data to socket
    :param socket: client socket
    :param data: string to send
    :param code: response code
    :param type: type of data
    """

    header = 'HTTP/1.1 {} {}\r\n'.format(code, HTTP_CODES[code])
    if data:
        header += 'Content-Type: {}\r\n'.format(type)
    header += 'Connection: close\r\n\r\n'

    writesocket(socket, header)
    if data:
        writesocket(socket, data)


def writesocket(socket, data, ip="", port=None):
    """
    sends data to socket
    :param socket: socket
    :param data: data to send
    :param ip: optional destination ip if socket is not bound
    :param port:  optional port if socket is not bound
    """
    if data:
        position = 0  # actual position in string
        datalen = len(data)  # total length of data
        poll = select.poll()
        poll.register(socket, select.POLLOUT)  # register write poll

        while position < datalen:
            try:
                if ip and port:
                    sent = socket.sendto(data[position:], (ip, port))
                else:
                    sent = socket.send(data[position:])  # sent & get number of bytes successfully sent
                position += sent
            except OSError as e:
                if e.args[0] == errno.ECONNRESET:  # connection aborted
                    break
                poll.poll()  # wait until socket is writeable again

        poll.unregister(socket)


def readsocket(socket):
    """
    Reads all available data from socket
    :param socket: socket
    :return: data bytestring
    """
    data = b""
    while True:
        try:
            chunk = socket.recv(512)
        except OSError:
            break
        if not chunk:
            break
        data += chunk
    return data


def gethttprequest(line):
    """
    parses first line of http header - request line
    :param line: string with line to parse
    :return: list [method, url, version]
    """
    if not line:  # blank line
        raise InvalidHeader

    header = line.strip()  # remove white chars and decode
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


def parseline(line):
    """
    parses line with header values of http
    :param line:
    :return: tuple (param, [values])
    """
    parts = line.strip().split(":", 1)  # param and values are separated by :
    param = None
    values = []

    if len(parts) > 0:
        param = parts[0].lower().strip()
    if len(parts) > 1:
        values = parts[1].split(";")  # each value is separated by ;
    return param, [v.strip() for v in values]  # remove white spaces for values
