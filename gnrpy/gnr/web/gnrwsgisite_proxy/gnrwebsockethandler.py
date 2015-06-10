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
from gnr.core.gnrbag import Bag
class WebSocketHandler(object):
    def __init__(self,site):
        self.site = site
        self.socket_path= os.path.join(gnrConfigPath(), 'sockets', '%s.tornado'% site.site_name)
        self.proxyurl='/wsproxy'
    
    @property
    def socketConnection(self):
        http_conn = HTTPSocketConnection(self.socket_path)
        http_conn.connect()
        return http_conn
        
    def sendCommandToPage(self,page_id,command,data):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        envelope=Bag(dict(command=command,data=data))
        body=urllib.urlencode(dict(page_id=page_id,envelope=envelope.toXml(unresolved=True)))
        self.socketConnection.request('POST',self.proxyurl,headers=headers, body=body)
        
    def setInClientData(self,page_id,path=None,data=None):
        self.sendCommandToPage(page_id,'set',Bag(data=data,path=path))
        
    def fireInClientData(self,page_id,path=None,data=None):
        self.sendCommandToPage(page_id,'set',Bag(data=data,path=path,fired=True))
        
    def publishToClient(self,page_id,topic=None,data=None):
        self.sendCommandToPage(page_id,'publish',Bag(data=data,topic=topic))

    #def sendDatachanges(self,datachanges):
    #    data=Bag()
    #    for j, change in enumerate(datachanges):
    #        data.setItem('sc_%i' % j, change.value, change_path=change.path, change_reason=change.reason,
    #                       change_fired=change.fired, change_attr=change.attributes,
    #                       change_ts=change.change_ts, change_delete=change.delete)
    #    self.sendCommandToPage(page_id,'datachanges',data)

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