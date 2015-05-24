#-*- coding: UTF-8 -*-  
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import httplib
import socket
import urllib
from gnr.app.gnrconfig import gnrConfigPath

class WebSocketHandler(object):
    def __init__(self,site):
        self.site = site
        
    def setInClientData(self,dest_page_id=None,client_path=None,data=None):
        socket_path= os.path.join(gnrConfigPath(), 'sockets', '%s.tornado'%self.site.site_name)
        http_conn = HTTPSocketConnection(socket_path)
        http_conn.connect()
        params = dict(client_path=client_path, page_id=dest_page_id, value=data)
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        result = http_conn.request('POST','/wsproxy',headers=headers, body=urllib.urlencode(params))
        return result


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
                print "HTTPSocketConnection - connect: (%s) ************" % (self.socket_path)
            self.sock.connect(self.socket_path)
        except socket.error, msg:
            if self.debuglevel > 0:
                print "HTTPSocketConnection - connect fail: (%s)" % (self.socket_path)
            if self.sock:
                self.sock.close()
            self.sock = None
        if not self.sock:
            raise socket.error, msg