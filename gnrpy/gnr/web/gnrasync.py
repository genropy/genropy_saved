# -*- coding: utf-8 -*-
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
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from past.builtins import basestring
#from builtins import object
import time
import os
import base64
from datetime import datetime
from copy import deepcopy
from functools import wraps
from concurrent.futures import ThreadPoolExecutor,Future
from tornado.concurrent import Future as TornadoFuture
import tornado.web
from tornado import gen,locks
import tornado.websocket as websocket
import tornado.ioloop
import signal
from tornado.netutil import bind_unix_socket
from tornado.tcpserver import TCPServer
from tornado.httpserver import HTTPServer

from gnr.core.gnrbag import Bag,TraceBackResolver
from gnr.web.gnrwsgisite_proxy.gnrwebsockethandler import AsyncWebSocketHandler
from gnr.web.gnrwsgisite import GnrWsgiSite
from gnr.core.gnrstring import fromJson
from tornado import version_info

if version_info[0]>=4 and version_info[1]>=2:
    from tornado import queues
else:
    import toro as queues

MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 3
    
def threadpool(func):
    func._executor='threadpool'
    return func

def lockedCoroutine(f):
    @wraps(f)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        with (yield self.lock.acquire()):
            result = f(self,*args, **kwargs)
            if isinstance(result,Future):
                yield result
    return wrapper

def lockedThreadpool(f):
    @wraps(f)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        with (yield self.lock.acquire()):
            yield self.server.executors['threadpool'].submit(f,self,*args,**kwargs)

    return wrapper
    
class GnrBaseHandler(object):
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
    def page_id(self):
        return getattr(self,'_page_id',None)
    
    @page_id.setter
    def page_id(self, page_id):
        self._page_id = page_id

    @property
    def gnrsite(self):
        return self.application.server.gnrsite

    @property
    def debug_queues(self):
        return self.application.server.debug_queues



        

class DebugSession(GnrBaseHandler):
    
    def __init__(self, stream, application):
        self.stream = stream
        self.application = application
        self.pdb_id = None
        self.page_id = None
        self.stream.set_close_callback(self.on_disconnect)
        self.socket_input_queue = queues.Queue(maxsize=40)
        self.socket_output_queue = queues.Queue(maxsize=40)
        self.websocket_output_queue = queues.Queue(maxsize=40)
        self.consume_socket_input_queue()

    def link_debugger(self, debugkey):
        page_id,pdb_id = debugkey.split(',')
        self.page_id = page_id
        self.pdb_id = pdb_id
        if debugkey not in self.debug_queues:
            self.debug_queues[debugkey] = queues.Queue(maxsize=40)
        self.websocket_input_queue = self.debug_queues[debugkey]
        self.consume_websocket_output_queue()
        self.consume_websocket_input_queue()
        self.consume_socket_output_queue()
    
    @gen.coroutine
    def handle_socket_message(self, message):
        if message.startswith('\0') or message.startswith('|'):
            self.link_debugger(message[1:])
        else:
            yield self.websocket_output_queue.put(message)


    @gen.coroutine
    def consume_socket_input_queue(self):
        while True:
            message = yield self.socket_input_queue.get()
            yield self.handle_socket_message(message)
 
    @gen.coroutine
    def consume_socket_output_queue(self):
        while True:
            message = yield self.socket_output_queue.get()
            yield self.stream.write(str("%s\n"%message))

    @gen.coroutine
    def consume_websocket_input_queue(self):
        while True:
            message = yield self.websocket_input_queue.get()
            yield self.socket_output_queue.put("%s"%message)

    @gen.coroutine
    def consume_websocket_output_queue(self):
        while True:
            data = yield self.websocket_output_queue.get()
            if data.startswith('B64:'):
                envelope = base64.b64decode(data[4:])
            else:
                data = Bag(dict(line=data,pdb_id=self.pdb_id))
                envelope = Bag(dict(command='pdb_out_line',data=data)).toXml()
            self.channels.get(self.page_id).write_message(envelope)
            
    @gen.coroutine 
    def on_disconnect(self):
        yield []
 
    @gen.coroutine 
    def dispatch_client(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                line = line[:-1]
                yield self.socket_input_queue.put(line)
        except tornado.iostream.StreamClosedError:
            pass
 
    @gen.coroutine 
    def on_connect(self):
        yield self.dispatch_client()

    
class GnrDebugServer(TCPServer):

    @gen.coroutine
    def handle_stream(self, stream, address):
        debug_session = DebugSession(stream, application = self.application)
        yield debug_session.on_connect()
        
class GnrWsProxyHandler(tornado.web.RequestHandler,GnrBaseHandler):

    def post(self, *args, **kwargs):
        page_id = self.get_argument('page_id')
        envelope = self.get_argument('envelope')
        if not page_id:
            envelope = Bag(envelope)
            command = envelope['command']
            data = envelope['data']
            self.server.externalCommand(command, data)
            return
        if page_id == '*':
            page_ids = list(self.channels.keys())
        else:
            page_ids = page_id.split(',')
        for dest_page_id in page_ids:
            self.channels.get(dest_page_id).write_message(envelope)

    def get(self, *args, **kwargs):
        pass

class GnrWebSocketHandler(websocket.WebSocketHandler,GnrBaseHandler):
    
    def getExecutor(self,method):
        executor = getattr(method,'_executor',None)
        if executor:
            return self.server.executors.get(executor)

    def getHandler(self,command,kwargs):
        if not '.' in command:
            return getattr(self,'do_%s' % command,self.wrongCommand) 
            
        kwargs['page_id']=self.page_id
        proxy=self.server        
        while '.' in command:
            proxyname,command=command.split('.',1)
            proxy=getattr(proxy,proxyname,None)
        if proxy is None:
            return self.wrongCommand
        return getattr(proxy,'do_%s' % command,self.wrongCommand) 

    def open(self):
        #print "WebSocket open - page_id:",self.page_id
        pass
        
    def close(self):
        #print "WebSocket close. page_id:",self.page_id
        pass
        
        
    @gen.coroutine 
    def on_message(self, message):
        command,result_token,kwargs=self.parseMessage(message)
        handler=self.getHandler(command,kwargs)
        if handler:
            executor=self.getExecutor(handler)
            if executor:
                result = yield executor.submit(handler,_time_start=time.time(),**kwargs)
            else:
                result = handler(_time_start=time.time(),**kwargs)
                if isinstance(result,Future):
                    result = yield result
                elif isinstance(result,TornadoFuture):
                    result = yield result
                    #result.add_done_callback(lambda f: self.tornado_future_result(f,result_token=result_token))
                    #yield None
            if result_token:
                result = Bag(dict(token=result_token,envelope=result)).toXml(unresolved=True)
            if result is not None:
                self.write_message(result)

    #def tornado_future_result(self,f,result_token=None):
    #    result = f.result()
    #    print 'tornado_future_result',result,result_token,f.done(),f.exc_info()
    #    result = Bag(dict(token=result_token,envelope=result)).toXml(unresolved=True)
    #    self.write_message(result)


    def on_close(self):
      #  print "WebSocket on_close",self.page_id
        self.channels.pop(self.page_id,None)
        self.server.unregisterPage(page_id=self.page_id)
        
    def check_origin(self, origin):
        return True
    
    def do_echo(self,data=None,**kwargs):
        return data
    
    def do_ping(self,lastEventAge=None,**kwargs):
        self.server.sharedStatus.onPing(self._page_id,lastEventAge)
        self.write_message('pong')
        
    def do_user_event(self,event=None,**kwargs):
        self.server.sharedStatus.onUserEvent(self._page_id,event)
        
    def do_route(self,target_page_id=None,envelope=None,**kwargs):
        websocket=self.channels.get(target_page_id)
        if websocket:
            websocket.write_message(envelope)

    def do_connected(self,page_id=None,**kwargs):
        self._page_id=page_id
        if page_id not in self.channels:
            #print 'setting in channels',self.page_id
            self.channels[page_id]=self
        else:
            pass
             #print 'already in channels',self.page_id
        if page_id not in self.pages:
            #print 'do_connected: missing page %s register it again' % page_id
            self.server.registerPage(page_id=page_id)
        else:
            pass
            #print 'already in pages',self.page_id

    #def do_som_command(self,cmd=None,_time_start=None,**kwargs):
    #    return self.server.som(cmd,page_id=self._page_id,**kwargs)
    #
    def do_pdb_command(self, cmd=None, pdb_id=None,**kwargs):
        #self.debugger.put_data(data)
        print('CMD',cmd)
        debugkey = '%s,%s' %(self.page_id,pdb_id)
        if debugkey not in self.debug_queues:
            self.debug_queues[debugkey] = queues.Queue(maxsize=40)
        data_queue = self.debug_queues[debugkey]
        data_queue.put(cmd)
        
    @threadpool
    def do_call(self,method=None,_time_start=None,**kwargs):
        error = None
        result = None
        resultAttrs=None
        handler = self.page.getWsMethod(method)

        self.page._db = None
        handler = self.page.getWsMethod(method)
        if handler:
            try:
                result = handler(**kwargs)
                if isinstance(result,tuple):
                    result,resultAttrs=result
            except Exception as e:
                result = TraceBackResolver()()
                error=str(e)
        envelope=Bag()
        
        envelope.setItem('data',result,_attributes=resultAttrs, _server_time=time.time()-_time_start)
        if error:
            envelope.setItem('error',error)  
        return envelope        
        #result=Bag(dict(token=result_token,envelope=envelope))
        #return result.toXml(unresolved=True)

        

    def wrongCommand(self,command=None,**kwargs):
        return 'WRONG COMMAND: %s' % command
        
    def parseMessage(self, message):
        kwargs=fromJson(message)
        catalog = self.server.gnrapp.catalog
        result = dict()
        for k, v in list(kwargs.items()):
            k = k.strip()
            if isinstance(v, basestring):
                try:
                    v = catalog.fromTypedText(v)
                    if isinstance(v, basestring):
                        v = v.decode('utf-8')
                    result[k] = v
                except Exception:
                    raise
            else:
                result[k] = v
        command = result.pop('command')
        result_token = result.pop('result_token',None)
        return command,result_token,result
       

class SharedObject(object):
    default_savedir = 'site:async/sharedobjects'
    def __init__(self,manager,shared_id,expire=None,startData=None,read_tags=None,write_tags=None,
                    filepath=None, dbSaveKw=None, saveInterval=None, autoSave=None, autoLoad=None,**kwargs):

        self.manager = manager
        self.lock=locks.Lock()
        self.server = manager.server
        self.shared_id = shared_id
        self._data = Bag(dict(root=Bag(startData)))
        self.read_tags = read_tags
        self.write_tags = write_tags
        self._data.subscribe('datachanges', any=self._on_data_trigger)
        self.subscribed_pages = dict()
        self.expire = expire or 0
        self.focusedPaths = {}
        if self.expire<0:
            self.expire = 365*24*60*60
        self.timeout=None
        self.autoSave=autoSave
        self.saveInterval=saveInterval
        self.autoLoad=autoLoad
        self.changes=False
        self.dbSaveKw=dbSaveKw
        self.onInit(**kwargs)


    @property
    def savepath(self):
        return self.server.gnrsite.storageNode(self.default_savedir,'%s.xml' %self.shared_id)

    @property
    def data(self):
        return self._data['root']

    @property
    def sql_data_column(self):
        return self.dbSaveKw.get('data_column') or 'shared_data'

    @property
    def sql_backup_column(self):
        return self.dbSaveKw.get('backup_column') or 'shared_backup'


    @lockedThreadpool
    def save(self):
        if self.changes :
            if self.dbSaveKw:
                kw = dict(self.dbSaveKw)
                tblobj = self.server.db.table(kw.pop('table'))
                handler = getattr(tblobj, 'saveSharedObject', None)
                if handler:
                    handler(self.shared_id, self.data, **kw)
                else:
                    self.sql_save(tblobj)
                self.server.db.commit()
            else:
                with self.savepath.open(mode='wb') as savefile:
                    self.data.toXml(savefile,unresolved=True,autocreate=True)
        self.changes=False

    @lockedThreadpool
    def load(self):
        if self.dbSaveKw:
            tblobj = self.server.db.table(self.dbSaveKw['table'])
            handler = getattr(tblobj, 'loadSharedObject', None)
            if handler:
                data = handler(self.shared_id)
            else:
                data = self.sql_load(tblobj)
        elif self.savepath.exists:
            with self.savepath.open(mode='r') as savefile:
                data =  Bag(savefile)
        else:
            data = Bag()
        self._data['root'] = data
        self.changes=False

    def sql_save(self, tblobj):
        backup = self.dbSaveKw.get('backup')
        data_column = self.sql_data_column
        with tblobj.recordToUpdate(self.shared_id) as record:
            if not self.data:
                print('NO DATA IN SAVING', self.shared_id)
            record[data_column] = deepcopy(self.data)
            onSavingHandler=getattr(tblobj, 'shared_onSaving',None)
            if onSavingHandler:
                onSavingHandler(record)

            if backup:
                backup_column = self.sql_backup_column
                if not record[backup_column]:
                    record[backup_column] =  Bag()
                    n = 0
                else:
                    n = int(list(record[backup_column].keys())[-1].split('_')[1])+1
                record[backup_column].setItem('v_%s' % n, record[data_column], ts=datetime.now())
                if len (record[backup_column]) > backup:
                    record[backup_column].popNode('#0')
            

    def sql_load(self, tblobj, version=None):
        record = tblobj.record(self.shared_id).output('bag')
        onLoadingHandler=getattr(tblobj, 'shared_onLoading',None)
        if onLoadingHandler:
            onLoadingHandler(record)

        if not version:
            return record[self.sql_data_column]
        else:
            return record[self.sql_backup_column].getItem('v_%i'% version)



    def onInit(self,**kwargs):
        if self.autoLoad:
            self.load()
        
    def onSubscribePage(self,page_id):
        pass
        #print 'onSubscribePage',self.shared_id,page_id
        
    def onUnsubscribePage(self,page_id):
        pass
        #print 'onUnsubscribePage',self.shared_id,page_id
    
    def onDestroy(self):
        print('onDestroy',self.shared_id)
        if self.autoSave:
            self.save()
        
        
    def onShutdown(self):
        if self.autoSave:
            self.save()
            
    def subscribe(self,page_id=None,**kwargs):
        page = self.server.pages[page_id]
        privilege= self.checkPermission(page)
        if privilege:
            page.sharedObjects.add(self.shared_id)
            subkwargs=dict(kwargs)
            subkwargs['page_id']=page_id
            subkwargs['user']=page.user
            self.subscribed_pages[page_id] = subkwargs
            self.server.sharedStatus.sharedObjectSubscriptionAddPage(self.shared_id,page_id,subkwargs)
            self.onSubscribePage(page)
            result=dict(privilege=privilege,data=self.data)
            return result

    def unsubscribe(self,page_id=None):
        self.subscribed_pages.pop(page_id,None)
        self.server.sharedStatus.sharedObjectSubscriptionRemovePage(self.shared_id,page_id)
        self.onUnsubscribePage(page_id)
        if not self.subscribed_pages:
            self.timeout=self.server.delayedCall(self.expire,self.manager.removeSharedObject,self)
            
    def checkPermission(self,page):
        privilege = 'readwrite' 
        if self.read_tags and not self.server.gnrapp.checkResourcePermission(self.read_tags,page.userTags):
            privilege = None
        elif self.write_tags and not self.server.gnrapp.checkResourcePermission(self.write_tags,page.userTags):
            privilege = 'readonly'
        return privilege
    
    @lockedCoroutine
    def datachange(self,page_id=None,path=None,value=None,attr=None,evt=None,fired=None,**kwargs):
        if fired:
            data = Bag(dict(value=value,attr=attr,path=path,shared_id=self.shared_id,evt=evt,fired=fired))
            self.broadcast(command='som.sharedObjectChange',data=data,from_page_id=page_id)
        else:
            path = 'root' if not path else 'root.%s' %path
            if evt=='del':
                self._data.popNode(path,_reason=page_id)
            else:
                self._data.setItem(path,value,_attributes=attr,_reason=page_id)

    def _on_data_trigger(self, node=None, ind=None, evt=None, pathlist=None,reason=None, **kwargs):
        self.changes=True
        if reason=='autocreate':
            return
        plist = pathlist[1:]
        if evt=='ins' or evt=='del':
            plist = plist+[node.label]
        path = '.'.join(plist)
        data = Bag(dict(value=node.value,attr=node.attr,path=path,shared_id=self.shared_id,evt=evt))
        from_page_id = reason
        self.broadcast(command='som.sharedObjectChange',data=data,from_page_id=from_page_id)

                
    def onPathFocus(self, page_id=None,curr_path=None,focused=None):
        if focused:
            self.focusedPaths[curr_path]=page_id
        else:
            self.focusedPaths.pop(curr_path,None)
        self.broadcast(command='som.onPathLock',from_page_id=page_id,data=Bag(dict(locked=focused,lock_path=curr_path)))

    
    def broadcast(self,command=None, data=None, from_page_id=None,):
        envelope = Bag(dict(command=command,data=data)).toXml()
        channels = self.server.channels
        for p in list(self.subscribed_pages.keys()):
            if p != from_page_id:
                channels.get(p).write_message(envelope)
        

class SqlSharedObject(SharedObject):

    pass
        

class SharedLogger(SharedObject):
    
    def onInit(self,**kwargs):
        print('onInit',self.shared_id)
        
    def onSubscribePage(self,page_id):
        print('onSubscribePage',self.shared_id,page_id)
        
    def onUnsubscribePage(self,page_id):
        print('onUnsubscribePage',self.shared_id,page_id)
    
    def onDestroy(self):
        print('onDestroy',self.shared_id)
    
   
class SharedStatus(SharedObject):
    def onInit(self,**kwargs):
        self.data['users']=Bag()
        self.data['sharedObjects']=Bag()

    @property
    def users(self):
        return self.data['users']
    @property
    def sharedObjects(self):
        return self.data['sharedObjects']

    def registerPage(self,page):
        page_item = page.page_item
        users = self.users
        page_id = page.page_id
        if page.user not in users:
            users[page.user] = Bag(dict(start_ts=page_item['start_ts'],user=page.user,connections=Bag()))
        userbag = users[page.user]
        connection_id = page.connection_id
        if connection_id not in userbag['connections']:
            userbag['connections'][connection_id] = Bag(dict(start_ts=page_item['start_ts'],
                                                        user_ip=page_item['user_ip'],
                                                        user_agent=page_item['user_agent'],
                                                        connection_id=connection_id,
                                                        pages=Bag()))
        userbag['connections'][connection_id]['pages'][page_id] = Bag(dict(pagename=page_item['pagename'],
                                                                            relative_url=page_item['relative_url'],
                                                                            start_ts=page_item['start_ts'],
                                                                            page_id=page_id))

    def unregisterPage(self,page):
        users = self.users
        userbag = users[page.user]
        connection_id = page.connection_id
        userconnections = userbag['connections']
        connection_pages = userconnections[connection_id]['pages']
        connection_pages.popNode(page.page_id)
        if not connection_pages:
            userconnections.popNode(connection_id)
            if not userconnections:
                users.popNode(page.user)


    def onPing(self,page_id,lastEventAge):
        page = self.server.pages.get(page_id)
        if page:
            userdata=self.users[page.user]
            conndata=userdata['connections'][page.connection_id]
            pagedata=conndata['pages'][page_id]
            pagedata['lastEventAge']=lastEventAge
            conndata['lastEventAge']=min(conndata['pages'].digest('#v.lastEventAge'))
            userdata['lastEventAge']=min(userdata['connections'].digest('#v.lastEventAge'))
  
            
    def onUserEvent(self, page_id, event):
        page = self.server.pages.get(page_id)
        if page:
            pagedata = self.users[page.user]['connections'][page.connection_id]['pages'][page_id]
            old_targetId=pagedata['evt_targetId']
            for k,v in list(event.items()):
                pagedata['evt_%s' %k] = v
            if old_targetId==event['targetId']:
                if event['type']=='keypress':
                    pagedata['typing']=True
            else:
                pagedata['typing']=False
 
    def registerSharedObject(self, shared_id,sharingkw):
        self.sharedObjects[shared_id]=Bag(sharingkw)
        

    def unregisterSharedObject(self, shared_id):
        self.sharedObjects.pop(shared_id)
    

    def sharedObjectSubscriptionAddPage(self, shared_id,page_id, subkwargs): 
        self.sharedObjects[shared_id]['subscriptions'][page_id]=Bag(subkwargs)
    
    def sharedObjectSubscriptionRemovePage(self, shared_id,page_id): 
        self.sharedObjects[shared_id]['subscriptions'].pop(page_id,None)
    
class SharedObjectsManager(object):
    """docstring for SharedObjectsManager"""
    def __init__(self, server,gc_interval=5):
        self.server = server
        self.sharedObjects = dict()
        self.change_queue = queues.Queue(maxsize=100)
        

        
    def getSharedObject(self,shared_id,expire=None,startData=None,read_tags=None,write_tags=None, factory=SharedObject,**kwargs):
        if shared_id not in self.sharedObjects:
            self.sharedObjects[shared_id] = factory(self,shared_id=shared_id,expire=expire,startData=startData,
                                                                read_tags=read_tags,write_tags=write_tags,**kwargs)
            sharingkw=dict(kwargs)
            sharingkw.update(dict(shared_id=shared_id,expire=expire,read_tags=read_tags,write_tags=write_tags,subscriptions=Bag()))
            self.server.sharedStatus.registerSharedObject(shared_id,sharingkw)
        return self.sharedObjects[shared_id]
        
    def removeSharedObject(self,so):
        if so.onDestroy() != False:
            self.sharedObjects.pop(so.shared_id,None)
            self.server.sharedStatus.unregisterSharedObject(so.shared_id)
            
    def do_unsubscribe(self,shared_id=None,page_id=None,**kwargs):
        sharedObject = self.sharedObjects.get(shared_id)
        if sharedObject:
            self.sharedObjects[shared_id].unsubscribe(page_id=page_id)
            
    def do_subscribe(self,shared_id=None,page_id=None,**kwargs):
        sharedObject=self.getSharedObject(shared_id,**kwargs)
        subscription =  sharedObject.subscribe(page_id)
        if not subscription:
            subscription=dict(privilege='forbidden',data=Bag())
        elif sharedObject.timeout:
            sharedObject.timeout.cancel()
            sharedObject.timeout=None
            
        data =  Bag(dict(value=subscription['data'],shared_id=shared_id,evt='init',privilege=subscription['privilege']))
        envelope = Bag(dict(command='som.sharedObjectChange',data=data))
        return envelope


    def do_datachange(self,shared_id=None,**kwargs):
        if shared_id in self.sharedObjects:
            self.sharedObjects[shared_id].datachange(**kwargs)

    def do_saveSharedObject(self,shared_id=None,**kwargs):
        self.sharedObjects[shared_id].save()

    def do_loadSharedObject(self,shared_id=None,**kwargs):
        self.getSharedObject(shared_id).load()

    def do_dispatch(self,shared_id=None,so_method=None,so_pars=None,**kwargs):
        so = self.getSharedObject(shared_id)
        pars = so_pars or dict()
        result = getattr(so,so_method)(**pars)
        return result
    #    if isinstance(result,TornadoFuture):
    #        result.add_done_callback(self.return_result)
    #    else:
    #        return result
#
    #def return_result(self,future_instance):
    #    result = future_instance.result()
#


                    
    def onShutdown(self):
        for so in list(self.sharedObjects.values()):
            so.onShutdown()
            

        
    def do_onPathFocus(self,shared_id=None,page_id=None,curr_path=None,focused=None,**kwargs):
        self.sharedObjects[shared_id].onPathFocus(page_id=page_id,curr_path=curr_path,focused=focused)

#
   # @gen.coroutine
   # def consume_change_queue(self):
   #     while True:
   #         change =
   #         so = self.sharedObjects[shared_id]
#
   #         self.sharedObjects[shared_id].datachange(**kwargs)
   #         if not self.busy:
#
   #             change = yield self.change_queue.get()
   #         yield self.handle_socket_message(message)

class DelayedCall(object):
    
    def __init__(self,server,delay,cb,*args,**kwargs):
        self.server=server
        self.timeout=self.server.io_loop.call_later(delay, cb, *args, **kwargs)
        
    def cancel(self):
        self.server.io_loop.remove_timeout(self.timeout)
        
        
        
class GnrBaseAsyncServer(object):
    def __init__(self, port=None, instance=None, ssl_crt=None, ssl_key=None, web=None, autoreload=None,
        site_options=None):
        self.port=port
        self.handlers=[]
        self.executors=dict()
        self.channels = dict()
        self.pages = dict()
        self.debug_queues=dict()
        self.gnrsite=GnrWsgiSite(instance)
        self.instance_name = self.gnrsite.site_name
        self.gnrsite.ws_site = self
        self.gnrapp = self.gnrsite.gnrapp
        self.db = self.gnrapp.db
        self.ssl_key = ssl_key
        self.ssl_crt = ssl_crt
        self.wsk = AsyncWebSocketHandler(self)
        self.som = SharedObjectsManager(self)
        self.web = web
        self.site_options = site_options or dict()
        self.autoreload = autoreload
        self.interval = 1000
        self.io_loop =tornado.ioloop.IOLoop.instance()
        #sched = tornado.ioloop.PeriodicCallback(self.scheduler,self.interval)
        #sched.start()

    def delayedCall(self,delay,cb,*args,**kwargs):
        return DelayedCall(self,delay,cb,*args,**kwargs)
        
    def scheduler(self,*args,**kwargs):
        print('scheduler',args,kwargs)

    def externalCommand(self, command, data):
       # print 'receive externalCommand',command
        handler = getattr(self, 'do_%s'%command)
        handler(**data.asDict(ascii=True))


    def do_registerNewPage(self, page_id=None, page_info=None, class_info=None, init_info=None, mixin_set=None):
        if not class_info:
            #added because in some case missing class_info. We should wrap into a try
            return
        page = self.gnrsite.resource_loader.instantiate_page(page_id=page_id,class_info=class_info, init_info=init_info, page_info=page_info)
        self.registerPage(page)
   
    def registerPage(self,page=None,page_id=None):
        if not page:
            #print 'Trying to retrieve page %s in gnrdaemon register' %page_id
            page = self.gnrsite.resource_loader.get_page_by_id(page_id)
            if not page:
                print('     page %s not existing in gnrdaemon register' %page_id)
                return
            else:
                pass
                #print '     page %s restored succesfully from gnrdaemon register' %page_id
        page.asyncServer = self
        page.sharedObjects = set()
        self.pages[page.page_id] = page
        self.sharedStatus.registerPage(page)

    def unregisterPage(self,page_id):
        page=self.pages.get(page_id)
        if not page:
            return
        if page.sharedObjects:
            for shared_id in page.sharedObjects:
                self.som.sharedObjects[shared_id].unsubscribe(page_id)
        self.sharedStatus.unregisterPage(page)
        page = self.pages.pop(page_id,None)

    @property
    def sharedStatus(self):
        return self.som.getSharedObject('__global_status__',expire=-1,
                                                            read_tags='_DEV_,superadmin',
                                                            write_tags='__SYSTEM__',factory=SharedStatus)


    @property
    def errorStatus(self):
        return self.som.getSharedObject('__error_status__',expire=-1,startData=dict(users=Bag()),
                                                            read_tags='_DEV_,superadmin',
                                                            write_tags='__SYSTEM__',factory=SharedLogger)
    def addHandler(self,path,factory,options=None):
        if options:
            self.handlers.append((path,factory,options))
        else:
            self.handlers.append((path,factory))
        
    def addExecutor(self,name,executor):
        self.executors[name]=executor
        
    def start(self):
        self.tornadoApp=tornado.web.Application(self.handlers, autoreload=self.autoreload)
        self.tornadoApp.server=self
        if self.ssl_crt and self.ssl_key:
            import ssl
            ssl_options = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_options.load_cert_chain(self.ssl_crt,self.ssl_key)
        else:
            ssl_options = None
        server = HTTPServer(self.tornadoApp, ssl_options=ssl_options)
        if self.port:
            server.listen(int(self.port))
        sockets_dir = os.path.join(self.gnrsite.site_path, 'sockets')
        print('sockets_dir',sockets_dir)
        if not os.path.exists(sockets_dir):
            os.mkdir(sockets_dir)
        socket_path = os.path.join(sockets_dir, 'async.tornado')
        main_socket = bind_unix_socket(socket_path)
        os.chmod(socket_path, 0o666)
            #server = HTTPServer(self.tornadoApp)
        server.add_socket(main_socket)
        debug_socket_path = os.path.join(sockets_dir, 'debugger.tornado')
        debug_socket = bind_unix_socket(debug_socket_path)
        debug_server = GnrDebugServer(self.io_loop)
        #debug_server.listen(8888)
        debug_server.add_socket(debug_socket)
        debug_server.application = self.tornadoApp
        signal.signal(signal.SIGTERM, self.onSignal)
        signal.signal(signal.SIGINT, self.onSignal)
        self.io_loop.start()

    def onSignal(self,sig, frame):
        self.io_loop.add_callback(self.onShutdown)

        
    def onShutdown(self):
        self.som.onShutdown()
        deadline = time.time() + MAX_WAIT_SECONDS_BEFORE_SHUTDOWN
        io_loop = self.io_loop
        def stop_loop():
            now = time.time()
            if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
        stop_loop()

    def logToPage(self,page_id,**kwargs):
        self.pages[page_id].log(**kwargs)

class GnrAsyncServer(GnrBaseAsyncServer):
    def __init__(self,*args, **kwargs):
        super(GnrAsyncServer, self).__init__(*args, **kwargs)
        self.addExecutor('threadpool',ThreadPoolExecutor(max_workers=20))
        self.addHandler(r"/websocket", GnrWebSocketHandler)
        self.addHandler(r"/wsproxy", GnrWsProxyHandler)
        if self.web:
            import tornado.wsgi
            from .tornado_wsgi import WSGIHandler
            wsgi_gnrsite=GnrWsgiSite(self.instance_name, tornado=True, **self.site_options)
            with wsgi_gnrsite.register.globalStore() as gs:
                gs.setItem('RESTART_TS',datetime.now())
                
            #wsgi_app = tornado.wsgi.WSGIContainer(wsgi_gnrsite)
            #self.addHandler(r".*",tornado.web.FallbackHandler, dict(fallback=wsgi_app))
            self.addHandler(r".*",WSGIHandler, {'wsgi_application': wsgi_gnrsite})
    
    
if __name__ == '__main__':
    server=GnrAsyncServer(port=8888,instance='sandbox')
    server.start()
    
    
    

  