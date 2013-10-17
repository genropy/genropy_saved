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

import Pyro4
from datetime import datetime
from gnr.core.gnrbag import Bag,BagResolver
import re

PYRO_HOST = 'localhost'
PYRO_PORT = 40004
PYRO_HMAC_KEY = 'supersecretkey'

class BaseRegister(object):
    """docstring for BaseRegister"""
    def __init__(self, siteregister):
        self.siteregister = siteregister
        self.registerItems = dict() 
        self.itemsData = dict()
        self.itemsTS = dict()

    def addRegisterItem(self,register_item):
        self.registerItems[register_item['register_item_id']] = register_item

    def attachData(self,register_item_id,data):
        self.itemsData[register_item_id] = Bag(data)
        self.refresh(register_item_id)

    def refresh(self,register_item_id):
        self.itemsTS[register_item_id] = datetime.now()

    def getData(self,register_item_id):
        return self.itemsData[register_item_id]

    def getItem(self,register_item_id,include_data=False):
        item = self.registerItems.get(register_item_id)
        self.refresh(register_item_id)
        if item and include_data:
            item['data'] = self.getData(register_item_id)
        return item

    def exists(self,register_item_id):
        return register_item_id in self.registerItems

    def keys(self):
        return self.registerItems.keys()

    def items(self):
        return self.registerItems.items()

    def values(self):
        return self.registerItems.values()

    def dropItem(self,register_item_id):
        register_item = self.registerItems.pop(register_item_id,None)
        self.itemsData.pop(register_item_id,None)
        self.itemsTS.pop(register_item_id,None)
        return register_item



class UserRegister(BaseRegister):
    """docstring for UserRegister"""
    def create(self, user, user_id=None,user_name=None,user_tags=None,avatar_extra=None):
        register_item = dict(
                register_item_id=user,
                start_ts=datetime.now(),
                user=user,
                user_id=user_id,
                user_name=user_name,
                user_tags=user_tags,
                avatar_extra=avatar_extra)
        self.addRegisterItem(register_item)
        return register_item
        
    def drop(self,user):
        self.dropItem(user)

class ConnectionRegister(BaseRegister):
    """docstring for ConnectionRegister"""
    def create(self, connection_id, connection_name=None,user=None,user_id=None,
                            user_name=None,user_tags=None,user_ip=None,user_agent=None,browser_name=None):
        register_item = dict(
                register_item_id=connection_id,
                start_ts=datetime.now(),
                connection_name = connection_name,
                user= user, 
                user_id= user_id,
                user_name = user_name,
                user_tags = user_tags,
                user_ip=user_ip,
                user_agent=user_agent,
                browser_name=browser_name)

        self.addRegisterItem(register_item)
        return register_item

    def drop(self,register_item_id=None,cascade=None):
        register_item = self.dropItem(register_item_id)
        if cascade:
            user = register_item['user']
            keys = self.user_connection_keys(user)
            if not keys:
                self.siteregister.drop_user(user)

    def user_connection_keys(self,user):
        return [k for k,v in self.items() if v['user'] == user]

    def user_connection_items(self,user):
        return [(k,v) for k,v in self.items() if v['user'] == user]



    def connections(self,user=None):
        connections = self.values()
        if user:
            connections = [v for v in connections if v['user'] == user]
        return connections

class PageRegister(BaseRegister):
    """docstring for PageRegister"""
    def create(self, page_id,pagename=None,connection_id=None,subscribed_tables=None,user=None,user_ip=None,user_agent=None ,data=None):
        register_item_id = page_id
        start_ts = datetime.now()
        if subscribed_tables:
            subscribed_tables = subscribed_tables.split(',')
        register_item = dict(
                register_item_id=register_item_id,
                pagename=pagename,
                connection_id=connection_id,
                start_ts=start_ts,
                subscribed_tables=subscribed_tables or [],
                user=user,
                user_ip=user_ip,
                user_agent=user_agent,
                datachanges=list(),
                subscribed_paths=set()
                )
        if data:
            self.attachData(register_item_id,data)
        self.addRegisterItem(register_item)
        return register_item


    def drop(self,register_item_id=None,cascade=None):
        register_item = self.dropItem(register_item_id)
        if cascade:
            connection_id = register_item['connection_id']
            n = self.siteregister.connectionPagesKeys(connection_id)
            if not n:
                self.siteregister.drop_connection(connection_id)


    def subscribed_table_page_keys(self,table):
        return [k for k,v in self.items() if table in v['subscribed_tables']]

    def subscribed_table_page_items(self,table):
        return [(k,v) for k,v in self.items() if table in v['subscribed_tables']]

    def subscribed_table_pages(self,table):
        return [v for k,v in self.items() if table in v['subscribed_tables']]



    def connection_page_keys(self,connection_id):
        return [k for k,v in self.items() if v['connection_id'] == connection_id]

    def connection_page_items(self,connection_id):
        return [(k,v) for k,v in self.items() if v['connection_id'] == connection_id]

    def pages(self,connection_id=None,user=None):
        pages = self.values()
        if connection_id:
            pages = [v for v in pages if v['connection_id'] == connection_id]
        if user:
            pages = [v for v in pages if v['user'] == user]
        return pages


class SiteRegister(object):
    def __init__(self,server):
        self.server = server
        self.p_register = PageRegister(self)
        self.c_register = ConnectionRegister(self)
        self.u_register = UserRegister(self)

    def new_connection(self,connection_id,connection_name=None,user=None,user_id=None,
                            user_name=None,user_tags=None,user_ip=None,user_agent=None,browser_name=None,avatar_extra=None):
        assert not self.c_register.exists(connection_id), 'SITEREGISTER ERROR: connection_id %s already registered' % connection_id
        if not self.u_register.exists(user):
            self.new_user( user, user_id=user_id,user_name=user_name,user_tags=user_tags,avatar_extra=avatar_extra)
        connection_item = self.c_register.create(connection_id, connection_name=connection_name,user=user,user_id=user_id,
                            user_name=user_name,user_tags=user_tags,user_ip=user_ip,user_agent=user_agent,browser_name=browser_name)

        return connection_item


    def drop_page(self,page_id, cascade=None):
        return self.p_register.drop(page_id,cascade=cascade)   

    def drop_connection(self,connection_id,cascade=None):
        self.c_register.drop(connection_id,cascade=cascade)

    def drop_user(self,user):
        self.u_register.drop(user)

    def user_connection_keys(self,user):
        self.c_register.user_connection_keys(user)

    def user_connection_items(self,user):
        self.c_register.user_connection_items(user)

    def user_connections(self,user):
        self.c_register.user_connections(user)

    def connection_page_keys(self,connection_id):
        self.p_register.connection_page_keys(connection_id=connection_id)

    def connection_page_items(self,connection_id):
        self.p_register.connection_page_items(connection_id=connection_id)

    def connection_pages(self,connection_id):
        self.p_register.connection_pages(connection_id=connection_id)


    def new_page(self,page_id,pagename=None,connection_id=None,subscribed_tables=None,user=None,user_ip=None,user_agent=None ,data=None):
        page_item = self.p_register.create(page_id, pagename = pagename,connection_id=connection_id,user=user,
                                            user_ip=user_ip,user_agent=user_agent, data=data)
        return page_item


    def new_user(self,user=None, user_tags=None, user_id=None, user_name=None,
                               avatar_extra=None):
        user_item = self.u_register.create( user=user, user_tags=user_tags, user_id=user_id, user_name=user_name,
                               avatar_extra=avatar_extra)
        return user_item

    def subscribed_table_pages(self,table=None):
        return self.p_register.subscribed_table_pages(table)

    def pages(self, connection_id=None,user=None,index_name=None, filters=None):
        if index_name:
            print 'call subscribed_table_pages instead of pages'
            return self.subscribed_table_pages(index_name)
        pages = self.p_register.pages(connection_id=connection_id,user=user)
        if not filters or filters == '*':
            return pages

        fltdict = dict()
        for flt in filters.split(' AND '):
            fltname, fltvalue = flt.split(':', 1)
            fltdict[fltname] = fltvalue
        filtered = []

        def checkpage(page, fltname, fltval):
            value = page[fltname]
            if not value:
                return
            if not isinstance(value, basestring):
                return fltval == value
            try:
                return re.match(fltval, value)
            except:
                return False

        for  page in pages.items():
            page = Bag(page)
            for fltname, fltval in fltdict.items():
                if checkpage(page, fltname, fltval):
                    filtered.append(page)
        return filtered

    def page(self,page_id):
        return self.p_register.getItem(page_id)

    def connection(self,connection_id):
        return self.c_register.getItem(connection_id)

    def user(self,user):
        return self.u_register.getItem(user)


    def users(self,*args,**kwargs):
        return self.u_register.values()

    def connections(self,user=None):
        return self.c_register.connections(user=user)
 

    def change_connection_user(self, connection_id, user=None, user_tags=None, user_id=None, user_name=None,
                               avatar_extra=None):
        print 'aaaa'

        connection_item = self.connection(connection_id)

        olduser = connection_item['user']
        newuser_item = self.user(user)
        print 'bbb'
        if not newuser_item:
            newuser_item = self.new_user( user=user, user_tags=user_tags, user_id=user_id, user_name=user_name,
                               avatar_extra=avatar_extra)
        print 'ccc'

        connection_item['user'] = user
        connection_item['user_tags'] = user_tags
        connection_item['user_name'] = user_name
        connection_item['user_id'] = user_id
        connection_item['avatar_extra'] = avatar_extra
        print 'ddd'

        for p in self.pages(connection_id=connection_id):
            p['user'] = user
        print 'eee'

        if not self.c_register.connections(olduser):
            self.drop_user(olduser)

        print 'fff'


    ###################################### TO DO ######################################

    def refresh(self,*args,**kwargs):
        return self.siteregister.refresh(*args,**kwargs)

    def cleanup(self,*args,**kwargs):
        return self.siteregister.cleanup(*args,**kwargs)




  


    def debug(self,mode,name,*args,**kwargs):
        if not name in self.current:
            print 'external_%s' %mode,name,'ARGS',args,'KWARGS',kwargs
            self.current[name] = True

    def __getattr__(self,name):
        h = getattr(self.siteregister,name)
        if not callable(h):
            self.debug('property',name)
            return h
        def decore(*args,**kwargs):
            self.debug('callable',name,*args,**kwargs)
            return h(*args,**kwargs)
        return decore




################################### CLIENT ##########################################

class SiteRegisterClient(object):
 

    def __init__(self,site,host=None,port=None,hmac_key=None):
        self.site = site
        host = host or PYRO_HOST
        port = port or PYRO_PORT
        hmac_key = str(hmac_key or PYRO_HMAC_KEY)
        Pyro4.config.HMAC_KEY = hmac_key
        Pyro4.config.SERIALIZER = 'pickle'
        uri = 'PYRO:SiteRegister@%s:%i' %(host,int(port))
        print 'URI',uri
        self.siteregister =  Pyro4.Proxy(uri)

        #self.siteregister = SiteRegister(site)


    def new_page(self, page_id, page, data=None):
        return self.siteregister.new_page( page_id, pagename = page.pagename,connection_id=page.connection_id,user=page.user,
                                            user_ip=page.user_ip,user_agent=page.user_agent, data=data)


    def new_connection(self, connection_id, connection):
        return self.siteregister.new_connection(connection_id,connection_name = connection.connection_name,user=connection.user,
                                                    user_id=connection.user_id,user_tags=connection.user_tags,user_ip=connection.ip,browser_name=connection.browser_name,
                                                    user_agent=connection.user_agent,avatar_extra=connection.avatar_extra)

   # def page(self,*args,**kwargs):
   #     return self.siteregister.page(*args,**kwargs)


   #def drop_page(self,*args,**kwargs):
   #    return self.siteregister.drop_page(*args,**kwargs)   


   #def connection(self,*args,**kwargs):
   #    return self.siteregister.connection(*args,**kwargs)

    def pages(self,*args,**kwargs):
        pages =  self.siteregister.pages(*args,**kwargs)
        #adapt for old use 
        return self.adaptListToDict(pages)

    def connections(self,user=None):
        connections = self.siteregister.connections(user=user)
        return self.adaptListToDict(connections)


    def adaptListToDict(self,l):
        return dict([(c['register_item_id'],c) for c in l])

    def users(self,*args,**kwargs):
        users = self.siteregister.users(*args,**kwargs)
        #adapt for old use 
        return self.adaptListToDict(users)  


########################### NO REMAP ######################################

    def connectionStore(self,*args,**kwargs):
        return self.siteregister.connectionStore(*args,**kwargs)
        
    def pageStore(self,*args,**kwargs):
        return self.siteregister.pageStore(*args,**kwargs)        

    def userStore(self,*args,**kwargs):
        return self.siteregister.userStore(*args,**kwargs)  

############################## TO DO #######################################


    def refresh(self,*args,**kwargs):
        return self.siteregister.refresh(*args,**kwargs)

    def cleanup(self,*args,**kwargs):
        return self.siteregister.cleanup(*args,**kwargs)

    def change_connection_user(self,*args,**kwargs):
        return self.siteregister.change_connection_user(*args,**kwargs)    

 

    def _debug(self,mode,name,*args,**kwargs):
        print 'external_%s' %mode,name,'ARGS',args,'KWARGS',kwargs


    def __getattr__(self,name):
        h = getattr(self.siteregister,name)
        if not callable(h):
            self._debug('property',name)
            return h
        def decore(*args,**kwargs):
            self._debug('callable',name,*args,**kwargs)
            return h(*args,**kwargs)
        return decore


##############################################################################

class RegisterTester(object):
    """docstring for RegisterTester"""
    def __init__(self, oldregister):
        self.oldregister = oldregister
        self.newregister = SiteRegisterClient(oldregister.site)
        self.implemented = ['new_page','drop_page','page','pages',
                            'new_connection','drop_connection','connection','connections',
                            'new_user','drop_user','user','users',
                            'change_connection_user']

    def __getattr__(self,name):
        h = getattr(self.oldregister,name)
        if not name in self.implemented:
            print 'NOT IMPLEMENTED',name
            return h
        if not callable(h):
            self._debug('property',name)
            return h
        def decore(*args,**kwargs):
            getattr(self.newregister,name)(*args,**kwargs)
            return h(*args,**kwargs)
        return decore

class PyroServer(object):
    def __init__(self,port=None,host=None,hmac_key=None,compression=None,multiplex=None,timeout=None,polltimeout=None):
        self.siteregister = SiteRegister(self)
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        port=port or PYRO_PORT
        host=host or PYRO_HOST
        hmac_key=hmac_key or PYRO_HMAC_KEY
        Pyro4.config.HMAC_KEY = str(hmac_key)
        if compression:
            Pyro4.config.COMPRESSION = True
        if multiplex:
            Pyro4.config.SERVERTYPE = "multiplex"
        if timeout:
            Pyro4.config.TIMEOUT = timeout
        if polltimeout:
            Pyro4.config.POLLTIMEOUT = timeout
        self.daemon = Pyro4.Daemon(host=host,port=int(port))
        self.main_uri = self.daemon.register(self,'PyroServer')
        self.register_uri = self.daemon.register(self.siteregister,'SiteRegister')

        print "uri=",self.main_uri

    def start(self):
        self.daemon.requestLoop()



class RegisterResolver(BagResolver):
    classKwargs = {'cacheTime': 1,
                   'readOnly': False,
                   'user': None,
                   'connection_id': None,
                   '_page': None
    }
    classArgs = ['user']


    def load(self):
        if not self.user:
            return self.list_users()
        elif not self.connection_id:
            return self.list_connections(user=self.user)
        else:
            return self.list_pages(connection_id=self.connection_id)
    @property
    def register(self):
        return self._page.site.register.newregister

    def list_users(self):
        usersDict = self.register.users()
        result = Bag()
        for user, item_user in usersDict.items():
            item = Bag()
            data = item_user.pop('data', None)
            item_user.pop('datachanges', None)
            item_user.pop('datachanges_idx', None)
            #item['info'] = Bag([('%s-%s' % (k, str(v).replace('.', '_')), v) for k, v in item_user.items()])
            item['data'] = data
            item.setItem('connections', RegisterResolver(user=user), cacheTime=3)
            result.setItem(user, item, user=user)
        return result

    def list_connections(self, user):
        connectionsDict = self.register.connections(user=user)
        result = Bag()
        for connection_id, connection in connectionsDict.items():
            delta = (datetime.now() - connection['start_ts']).seconds
            user = connection['user'] or 'Anonymous'
            connection_name = connection['connection_name']
            itemlabel = '%s (%i)' % (connection_name, delta)
            item = Bag()
            data = connection.pop('data', None)
            #item['info'] = Bag([('%s:%s' % (k, str(v).replace('.', '_')), v) for k, v in connection.items()])
            item['data'] = data
            item.setItem('pages', RegisterResolver(user=user, connection_id=connection_id), cacheTime=2)
            result.setItem(itemlabel, item, user=user, connection_id=connection_id)
        return result

    def list_pages(self, connection_id):
        pagesDict = self.register.pages(connection_id=connection_id)
        result = Bag()
        for page_id, page in pagesDict.items():
            delta = (datetime.now() - page['start_ts']).seconds
            pagename = page['pagename'].replace('.py', '')
            itemlabel = '%s (%i)' % (pagename, delta)
            item = Bag()
            data = page.pop('data', None)
            #item['info'] = Bag([('%s:%s' % (k, str(v).replace('.', '_')), v) for k, v in page.items()])
            item['data'] = data
            result.setItem(itemlabel, item, user=item['user'], connection_id=item['connection_id'], page_id=page_id)
        return result     

    def resolverSerialize(self):
        attr = super(RegisterResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

if __name__ == '__main__':
    s = PyroServer()
    s.start()






