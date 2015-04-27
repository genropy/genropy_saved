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
from gnr.core.gnrbag import Bag,BagException
from gnr.app.gnrapp import GnrApp
from gnr.core.gnrstring import fromJson
from concurrent.futures import ThreadPoolExecutor,Future, Executor
from threading import Lock

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
            
class GnrWebSocketHandler(websocket.WebSocketHandler):
   
    @property
    def server(self):
        return self.application.server
        
    @property
    def channels(self):
        return self.application.server.channels
        
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
            result=yield executor.submit(handler,**kwargs)
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
       
    def do_disconnected(self,**kwargs):
        self.channels.pop(self.page_id,None)
    
    def do_channels(self,**kwargs):
        return self.channels.keys()
        
    def do_setInClient(self,dest_page_id=None,dest_path=None,value=None):
        message=dict(path=dest_path,data=data)
        self.channels.get(dest_page_id).write_message(message)
        
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
        self.gnrapp=GnrApp(instance)

    def addHandler(self,path,factory):
        self.handlers.append((path,factory))
        
    def addExecutor(self,name,executor):
        self.executors[name]=executor
        
    def start(self):
        self.tornadoApp=tornado.web.Application(self.handlers)
        self.tornadoApp.server=self
        self.tornadoApp.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
       

class GnrAsyncServer(GnrBaseAsyncServer):
    def __init__(self,*args, **kwargs):
        super(GnrAsyncServer, self).__init__(*args, **kwargs)
        self.addExecutor('threadpool',ThreadPoolExecutor(max_workers=20))
        self.addExecutor('dummy',DummyExecutor())
        self.addHandler(r"/", GnrWebSocketHandler)
        
    
if __name__ == '__main__':
    server=GnrAsyncServer(port=8888,instance='sandbox')
    server.start()
    
    
    

  