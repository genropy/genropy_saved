import httplib
import socket

def has_timeout(timeout): # python 2.6
    if hasattr(socket, '_GLOBAL_DEFAULT_TIMEOUT'):
        return (timeout is not None and timeout is not socket._GLOBAL_DEFAULT_TIMEOUT)
    return (timeout is not None)


class HTTPSocketConnection(httplib.HTTPConnection):
 
    def __init__(self, socket_path, host='127.0.0.1', port=None, strict=None,
                 timeout=None):
        self.socket_path=socket_path
        httplib.HTTPConnection.__init__(self, host, port=port, strict=strict, timeout=timeout)

    def connect(self):
        """Connect to the host and port specified in __init__."""
        # Mostly verbatim from httplib.py.
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if has_timeout(self.timeout):
                self.sock.settimeout(self.timeout)
            if self.debuglevel > 0:
                print "connect: (%s) ************" % (self.socket_path)
            self.sock.connect(self.socket_path)
        except socket.error, msg:
            if self.debuglevel > 0:
                print "connect fail: (%s)" % (self.socket_path)
            if self.sock:
                self.sock.close()
            self.sock = None
        if not self.sock:
            raise socket.error, msg
