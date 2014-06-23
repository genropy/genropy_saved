#!/usr/bin/env python

import getpass
import select
import SocketServer
import threading
import paramiko
import atexit
import thread
import re
CONN_STRING_RE=r"(?P<ssh_user>\w*)\:?(?P<ssh_password>\w*)\@(?P<ssh_host>(\w|\.)*)\:?(?P<ssh_port>\w*)"
CONN_STRING = re.compile(CONN_STRING_RE)


def normalized_sshtunnel_parameters(**options):
    connection_string = options.pop('ssh_host')
    match = re.search(CONN_STRING, connection_string)
    result = dict(
    ssh_user = match.group('ssh_user') or None,
    ssh_password = match.group('ssh_password') or None,
    ssh_host = match.group('ssh_host') or None,
    ssh_port = match.group('ssh_port') or '22')
    options = options or dict()
    for k,v in options.items():
        if v is not None:
            result[k] = v
    result['forwarded_host'] = options.get('forwarded_host') or '127.0.0.1'
    return result

class ForwardServer (SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    

class Handler (SocketServer.BaseRequestHandler):

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.forwarded_host, self.forwarded_port),
                                                   self.request.getpeername())
        except Exception:
            raise
        if chan is None:
            return

        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
        chan.close()
        self.request.close()
        

class IncompleteConfigurationException(Exception):
    pass

class SshTunnel(object):
    def __init__(self, local_port=0, forwarded_host='127.0.0.1', forwarded_port=None, ssh_host=None, ssh_port=22,
                username=None, password=None):
        self.forwarded_host = forwarded_host
        self.forwarded_port = forwarded_port
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self._local_port = local_port
        self.username = username
        self.password = password
        self.exit_event = threading.Event()

    @property
    def local_port(self):
        return self._local_port

    def prepare_tunnel(self):
        if not self.forwarded_host:
            raise IncompleteConfigurationException('Missing Forwarded Host')
        if not self.forwarded_port:
            raise IncompleteConfigurationException('Missing Forwarded Port')
        if not self.ssh_host:
            raise IncompleteConfigurationException('Missing Ssh Host')
        if not self.ssh_port:
            raise IncompleteConfigurationException('Missing Ssh Port')
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.client.connect(self.ssh_host, self.ssh_port, username=self.username,
                       look_for_keys=False, password=self.password)
        transport = self.client.get_transport()
            
        class SubHander (Handler):
            forwarded_host = self.forwarded_host
            forwarded_port = self.forwarded_port
            ssh_transport = transport
            exit_event = self.exit_event

        self.forwarding_server=ForwardServer(('', self.local_port), SubHander)
        self._local_port = self.forwarding_server.socket.getsockname()[1]

    def stop(self):
        self.forwarding_server.shutdown()

    def serve_tunnel(self):
        thread.start_new_thread(self._serve_tunnel,())

    def _serve_tunnel(self):
        self.forwarding_server.serve_forever()


def stop_tunnel(tunnel):
    tunnel.stop()

def main():
    server_host = 'genropy.org'
    server_port = 22
    password = None
    password = getpass.getpass('Enter SSH password: ')
    tunnel = SshTunnel(forwarded_port=22, ssh_host=server_host, ssh_port=server_port, username='genro', password=password)
    tunnel.prepare_tunnel()
    print tunnel.local_port
    tunnel.serve_tunnel()
    atexit.register(stop_tunnel, tunnel)
    password = getpass.getpass('any key to stop ')


if __name__ == '__main__':
    main()