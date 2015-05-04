# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrbag : an advanced data storage system
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
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

import tornado.web
from tornado import gen
import tornado.websocket as websocket
import tornado.ioloop
from tornado.netutil import bind_unix_socket
from tornado.httpserver import HTTPServer
from gnr.core.gnrbag import Bag,BagException
from gnr.web.gnrwsgisite import GnrWsgiSite
from gnr.core.gnrstring import fromJson
from concurrent.futures import ThreadPoolExecutor,Future, Executor
from threading import Lock
import os
from gnr.app.gnrconfig import gnrConfigPath
import time

def threadpool(func):
    func._executor='threadpool'
    return func
    
class DummyExecutor(Executor):
    def __init__(self):
        self._shutdown = False
        self._shutdownLock = Lock()
    def submit(self, fn, *args, **kwargs):
        with self._shutdownLock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = Future()
            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                f.set_exception(e)
            else:
                f.set_result(result)

            return f

    def shutdown(self, wait=True):
        with self._shutdownLock:
            self._shutdown = True
            

class GnrClientDataHandler(tornado.web.RequestHandler):

    @property
    def server(self):
        return self.application.server
        
    @property
    def channels(self):
        return self.application.server.channels
        
    #def post(self, dest_page_id, message):
    def post(self, *args, **kwargs):
        print self.request.body
        page_id = self.get_argument('page_id')
        print page_id
        client_path = self.get_argument('client_path')
        print client_path
        value = self.get_argument('value')
        print value
        data = Bag(path=client_path, data=value)
        message=Bag(data=data,command='set')
        message_xml = message.toXml()
        print message_xml
        if page_id == '*':
            page_ids = self.channels.keys()
        else:
            page_ids = page_id.split(',')
        for dest_page_id in page_ids:
            self.channels.get(dest_page_id).write_message(message_xml)
        #self.channels.get(dest_page_id).write_message(message)

    def get(self, *args, **kwargs):
        pass

class GnrWebSocketHandler(websocket.WebSocketHandler):
   
    @property
    def server(self):
        return self.application.server
        
    @property
    def channels(self):
        return self.application.server.channels

    @property
    def pages(self):
        return self.application.server.pages

    @property
    def page(self):
        return self.pages[self.page_id]
    
    
    @property
    def gnrsite(self):
        return self.application.server.gnrsite
    
    def getExecutor(self,method):
        return self.server.executors.get(getattr(method,'_executor','dummy'))

    def getHandler(self,command):
        return getattr(self,'do_%s' % command,self.wrongCommand)  
        
    def open(self):
        print "WebSocket opened"
        
    def close(self):
        print "WebSocket closed"
        
    @gen.coroutine 
    def on_message(self, message):
        command,kwargs=self.parseMessage(message)
        handler=self.getHandler(command)
        if handler:
            executor=self.getExecutor(handler)
            result=yield executor.submit(handler,_time1=time.time(),**kwargs)
            if result is not None:
                self.write_message(result)
                
    def on_close(self):
        print "WebSocket closed"
        
    def check_origin(self, origin):
        return True

    def do_echo(self,data=None,**kwargs):
        return data

    def do_connected(self,page_id=None,**kwargs):
        self.page_id=page_id
        self.channels[page_id]=self
        page = self.gnrsite.resource_loader.get_page_by_id(page_id)
        self.pages[page_id] = page
       
    def do_disconnected(self,**kwargs):
        self.channels.pop(self.page_id,None)
    
    def do_channels(self,**kwargs):
        return self.channels.keys()
        
    def do_setInClient(self,dest_page_id=None,dest_path=None,value=None):
        message=dict(path=dest_path,data=value)
        self.channels.get(dest_page_id).write_message(message)

    @threadpool
    def do_wsmethod(self,method=None, dest_path=None, err_path = None,_time1=None,**kwargs):
        error = None
        result = None

        handler = self.page.getWsMethod(method)
        if handler:
            try:
                result = handler(**kwargs)
            except Exception, e:
                error = str(e)
        data=Bag()
        if error:
            result =error 
            dest_path = err_path or 'gnr.websocket_error.%s'%method.replace('.','_').replace(':','_')

        data.setItem('path',dest_path)
        data.setItem('data',result, server_time=time.time()-_time1)
        return self.serializeMessage(command='set',data=data)
        

    def serializeMessage(self,command=None,data=None):
        result=Bag(dict(command=command,data=data))
        print result
        return result.toXml(unresolved=True)
        
    @threadpool
    def do_getRecord(self,table=None,pkey=None,dest_path=None,**kwargs):
        table=self.server.gnrapp.db.table(table)
        record=table.record(pkey,ignoreMissing=True).output('bag', resolver_one='relOneResolver', resolver_many='relManyResolver')
        data=Bag()
        caption=table.recordCaption(record)
        data.setItem('path',dest_path)
        data.setItem('data',record,caption=caption)
        
        return self.serializeMessage(command='set',data=data)
   
        
    def wrongCommand(self,command=None,**kwargs):
        return 'WRONG COMMAND: %s' % command
        
    def parseMessage(self, message):
        kwargs=fromJson(message)
        catalog = self.server.gnrapp.catalog
        result = dict()
        for k, v in kwargs.items():
            k = k.strip()
            if isinstance(v, basestring):
                try:
                    v = catalog.fromTypedText(v)
                    if isinstance(v, basestring):
                        v = v.decode('utf-8')
                    result[k] = v
                except Exception, e:
                    raise
            else:
                result[k] = v
        command=result.pop('command')
        return command,result
       

class GnrBaseAsyncServer(object):
    def __init__(self,port=None,instance=None):
        self.port=port
        self.handlers=[]
        self.executors=dict()
        self.channels=dict()
        self.pages=dict()
        self.instance_name = instance
        self.gnrsite=GnrWsgiSite(instance)
        self.gnrsite.ws_site = self
        self.gnrapp = self.gnrsite.gnrapp

    def addHandler(self,path,factory):
        self.handlers.append((path,factory))
        
    def addExecutor(self,name,executor):
        self.executors[name]=executor
        
    def start(self):
        self.tornadoApp=tornado.web.Application(self.handlers)
        self.tornadoApp.server=self
        if self.port:
            self.tornadoApp.listen(int(self.port))
        else:
            socket_path = os.path.join(gnrConfigPath(), 'sockets', '%s.tornado'%self.instance_name)
            socket = bind_unix_socket(socket_path)
            server = HTTPServer(self.tornadoApp)
            server.add_socket(socket)
        tornado.ioloop.IOLoop.instance().start()
       

class GnrAsyncServer(GnrBaseAsyncServer):
    def __init__(self,*args, **kwargs):
        super(GnrAsyncServer, self).__init__(*args, **kwargs)
        self.addExecutor('threadpool',ThreadPoolExecutor(max_workers=20))
        self.addExecutor('dummy',DummyExecutor())
        self.addHandler(r"/websocket", GnrWebSocketHandler)
        self.addHandler(r"/set_in_client_data", GnrClientDataHandler)
        
    
if __name__ == '__main__':
    server=GnrAsyncServer(port=8888,instance='sandbox')
    server.start()
    
    
    

  