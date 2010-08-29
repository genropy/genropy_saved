# -*- coding: UTF-8 -*-
# 
"""Registered users tester"""
import datetime
from gnr.core.gnrbag import Bag,BagResolver
class GnrCustomWebPage(object):
    py_requires="testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme='claro'
    
    def test_1_registered_users(self,pane):
        """Users tree"""
        bc = pane.borderContainer(height='500px',datapath='test1')
        left = bc.contentPane(region='left',width='250px',splitter=True)
        left.dataRemote('.curr_users.users','curr_users',cacheTime=2)
        left.tree(storepath='.curr_users',selected_user='^.user')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='4px')
        fb.div('^.user',lbl='Selected user')
        fb.textbox(value='^.path',lbl='Path')
        fb.textbox(value='^.value',lbl='Value')
        fb.button('Send',fire='.send')
        center.dataRpc('dummy','send_data_to_user',
                        v='=.value',p='=.path',_fired='^.send',
                        user='=.user')
        

    def rpc_send_data_to_user(self,v=None,p=None,user=None):
        user = user or self.user
        with self.userStore(user=user) as store:
            store.setItem(p,v)
            
        
    def rpc_curr_users(self):
        return UserListResolver()
        
class UserListResolver(BagResolver):
    classKwargs={'cacheTime':1,
                 'readOnly':False,
                 'connectionId':None,
                 'user':None}
    classArgs=['user']
        

    def load(self):   
        if not self.user:
            return self.list_users()
        else:
            return self.one_user()
            
    def one_user(self):        
        register = self._page.site.register_user
        item_user = register.get_register_item(self.user)
        item = Bag()
        data = item_user.pop('data',None)
        item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in item_user.items()])
        item['data'] = data
        item.setItem('connections',ConnectionListResolver(),cacheTime=2)
        return item
        
    def list_users(self):
        usersDict = self._page.site.register_user.users()
        result = Bag()
        for user,item_user in usersDict.items():
            delta = (datetime.datetime.now()-item_user['start_ts']).seconds
            user = user or 'Anonymous'
            itemlabel = user
            resolver = UserListResolver(user)
            result.setItem(itemlabel,resolver,cacheTime=1,user=user)
        return result 

class ConnectionListResolver(BagResolver):
    classKwargs={'cacheTime':1,
                 'readOnly':False,
                 'connectionId':None}
    classArgs=['connectionId']
    def load(self):
        if not self.connectionId:
            return self.list_connections()
        else:
            return self.one_connection()
            
    def one_connection(self):        
        register = self._page.site.register_connection
        page = register.get_register_item(self.connectionId)
        item = Bag()
        data = page.pop('data',None)
        item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in page.items()])
        item['data'] = data
        item.setItem('pages',PageListResolver(),cacheTime=2)
        return item
        
    def list_connections(self):
        connectionsDict = self._page.site.register_connection.connections()
        result = Bag()
        for connection_id,connection in connectionsDict.items():
            delta = (datetime.datetime.now()-connection['start_ts']).seconds
            user = connection['user'] or 'Anonymous'
            ip =  connection['user_ip'].replace('.','_')
            connection_name=connection['connection_name']
            user_agent=connection['user_agent']
            itemlabel = '%s (%i)' %(connection_name,delta)
            resolver = ConnectionListResolver(connection_id)
            result.setItem(itemlabel,resolver,cacheTime=1,connection_id=connection_id)
        return result 

class PageListResolver(BagResolver):
    classKwargs={'cacheTime':1,
                 'readOnly':False,
                 'pageId':None}
    classArgs=['pageId']
    def load(self):
        if not self.pageId:
            return self.list_pages()
        else:
            return self.one_page()
    
    def one_page(self):
        register = self._page.site.register_page
        page = register.get_register_item(self.pageId)
        item = Bag()
        data = page.pop('data',None)
        item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in page.items()])
        item['data'] = data
        return item
        
    def list_pages(self):
        pagesDict = self._page.site.register_page.pages()
        result = Bag()
        for page_id,page in pagesDict.items():
            delta = (datetime.datetime.now()-page['start_ts']).seconds
            pagename= page['pagename'].replace('.py','')
            itemlabel = '%s (%i)' %(pagename,delta)
            resolver = PageListResolver(page_id)
            result.setItem(itemlabel,resolver,cacheTime=1)
        return result 
