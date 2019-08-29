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

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
#from builtins import object
import os
import http.client
import socket
import urllib.request, urllib.parse, urllib.error
from gnr.core.gnrbag import Bag

from time import sleep
CONNECTION_REFUSED = 61
MAX_CONNECTION_ATTEMPT = 20 
CONNECTION_ATTEMPT_DELAY = 1


class WebSocketHandler(object):
    def sendCommandToPage(self,page_id,command,data):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        envelope=Bag(dict(command=command,data=data))
        body=urllib.parse.urlencode(dict(page_id=page_id,envelope=envelope.toXml(unresolved=True)))
        self.socketConnection.request('POST',self.proxyurl,headers=headers, body=body)
        
    def setInClientData(self,page_id,path=None,value=None,nodeId=None,
                    attributes=None,fired=None,reason=None,noTrigger=None):
        if not isinstance(page_id,list):
            page_id = [page_id]
        for p in page_id:
            self.sendCommandToPage(p,'setInClientData',Bag(dict(value=value,path=path,attributes=attributes,reason=reason,nodeId=nodeId,noTrigger=noTrigger)))
        
    def fireInClientData(self,page_id,path=None,data=None):
        self.sendCommandToPage(page_id,'set',Bag(data=data,path=path,fired=True))
        
    def publishToClient(self,page_id,topic=None,data=None,nodeId=None,iframe=None,parent=None):
        self.sendCommandToPage(page_id,'publish',Bag(data=data, topic=topic, nodeId=nodeId, iframe=iframe, parent=parent))

    #def sendDatachanges(self,datachanges):
    #    data=Bag()
    #    for j, change in enumerate(datachanges):
    #        data.setItem('sc_%i' % j, change.value, change_path=change.path, change_reason=change.reason,
    #                       change_fired=change.fired, change_attr=change.attributes,
    #                       change_ts=change.change_ts, change_delete=change.delete)
    #    self.sendCommandToPage(page_id,'datachanges',data)


class AsyncWebSocketHandler(WebSocketHandler):
    def __init__(self,server):
        self.server = server

    def sendCommandToPage(self,page_id,command,data):
        envelope = Bag(dict(command=command,data=data))
        self.server.channels.get(page_id).write_message(envelope.toXml(unresolved=True))


class WsgiWebSocketHandler(WebSocketHandler):
    def __init__(self,site):
        self.site = site
        sockets_dir = os.path.join(site.site_path, 'sockets')
        if not os.path.exists(sockets_dir):
            os.mkdir(sockets_dir)
        self.socket_path= os.path.join(sockets_dir, 'async.tornado')
        self.proxyurl='/wsproxy'
    
    def checkSocket(self):
        try:
            self.socketConnection
            return True
        except socket.error as e:
            if e.errno == CONNECTION_REFUSED:
                return False
        

    @property
    def socketConnection(self):
        http_conn = HTTPSocketConnection(self.socket_path,timeout=1000)
        http_conn.connect()
        return http_conn
        
    def sendCommandToPage(self,page_id,command,data):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        envelope=Bag(dict(command=command,data=data))

        body = urllib.parse.urlencode(dict(page_id=page_id,envelope=envelope.toXml(unresolved=True)))
        #self.socketConnection.request('POST',self.proxyurl,headers=headers, body=body)

        n = MAX_CONNECTION_ATTEMPT
        error = CONNECTION_REFUSED
        while n>0 and error==CONNECTION_REFUSED:
            try:
                self.socketConnection.request('POST',self.proxyurl,headers=headers, body=body)
                error = False
                if n!=MAX_CONNECTION_ATTEMPT:
                    print('SUCCEED')
            except socket.error as e:
                error = e.errno
                if error == CONNECTION_REFUSED:
                    n -= 1
                    print('attempting',n)
                    sleep(CONNECTION_ATTEMPT_DELAY)
                else:
                    raise




def has_timeout(timeout): # python 2.6
    if hasattr(socket, '_GLOBAL_DEFAULT_TIMEOUT'):
        return (timeout is not None and timeout is not socket._GLOBAL_DEFAULT_TIMEOUT)
    return (timeout is not None)


    
class HTTPSocketConnection(http.client.HTTPConnection):
 
    def __init__(self, socket_path, host='127.0.0.1', port=None,
                 timeout=None):
        self.socket_path=socket_path
        http.client.HTTPConnection.__init__(self, host, port=port, timeout=timeout)

    def connect(self):
        """Connect to the host and port specified in __init__."""
        # Mostly verbatim from httplib.py.
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            if has_timeout(self.timeout):
                self.sock.settimeout(self.timeout)
            if self.debuglevel > 0:
                print("HTTPSocketConnection - connect: (%s) ************" % (self.socket_path))
            self.sock.connect(self.socket_path)
        except socket.error as msg:
            if self.debuglevel > 0:
                print("HTTPSocketConnection - connect fail: (%s)" % (self.socket_path))
            if self.sock:
                self.sock.close()
            self.sock = None
            if not self.sock:
                raise socket.error(msg)

