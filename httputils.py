import select
import errno

HTTP_CODES = {200: "OK",
              400: "Bad Request",
              404: "Not Found"}
TYPE_JSON = "application/json"
TYPE_HTML = "text/html"


class InvalidHeader(Exception):
    pass

def sendpage(socket, file):
    """
    sends web page read from file into a socket
    :param socket: client socket
    :param file: file name
    """
    with open(file, "r") as f:
        while True:
            data = file.read(512)
            if not data:
                break
            response(socket, data)

def response(socket, data="", code=200, type=TYPE_HTML):
    """
    sends response with data to socket
    :param socket: client socket
    :param data: string to send
    :param code: response code
    :param type: type of data
    """
    socket.send('HTTP/1.1 {} {}\n'.format(code, HTTP_CODES[code]))
    if data:
        socket.send('Content-Type: {}\n'.format(type))
    socket.send('Connection: close\n\n')

    if data:
        position = 0  # actual position in string
        datalen = len(data)  # total length of data
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


def getrequest(line):
    """
    parses first line of http header - request line
    :param line:
    :return: list [method, url, version]
    """
    if not line:  # blank line
        raise InvalidHeader

    header = line.decode('utf-8').strip()  # remove white chars and decode
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
    parses line with values of http
    :param line:
    :return: list [param, [values]]
    """
    parts = line.strip().split(":")  # param and values are separated by :
    if len(parts) > 1:
        param = parts[0].lower()
        values = "".join(parts[1:]).split(";")  # each value is separated by ;
        return (param, [v.strip() for v in values])  # remove white spaces for values
    return (None, [])
