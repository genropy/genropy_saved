# -*- coding: UTF-8 -*-

"""Registered connections tester"""

import datetime
from gnr.core.gnrbag import Bag, BagResolver

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme = 'claro'
    
    def test_1_registered_connections(self, pane):
        """Connections tree"""
        bc = pane.borderContainer(height='500px', datapath='test1')
        left = bc.contentPane(region='left', width='250px', splitter=True)
        left.dataRemote('.curr_connections.connections', 'curr_connections', cacheTime=2)
        left.tree(storepath='.curr_connections', selected_connection_id='^.connection_id')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='4px')
        fb.div('^.connection_id', lbl='Selected connection')
        fb.textbox(value='^.path', lbl='Path')
        fb.textbox(value='^.value', lbl='Value')
        fb.button('Send', fire='.send')
        center.dataRpc('dummy', 'send_data_to_connection',
                       v='=.value', p='=.path', _fired='^.send',
                       connection_id='=.connection_id')
                       
    def rpc_send_data_to_connection(self, v=None, p=None, connection_id=None):
        connection_id = connection_id or self.connection_id
        with self.connectionStore(connection_id=connection_id) as store:
            store.setItem(p, v)
            
    def rpc_curr_connections(self):
        return ConnectionListResolver()
        
class ConnectionListResolver(BagResolver):
    classKwargs = {'cacheTime': 1,
                   'readOnly': False,
                   'connectionId': None}
    classArgs = ['connectionId']
    
    def load(self):
        if not self.connectionId:
            return self.list_connections()
        else:
            return self.one_connection()
            
    def one_connection(self):
        register = self._page.site.register_connection
        page = register.get_register_item(self.connectionId)
        item = Bag()
        data = page.pop('data', None)
        item['info'] = Bag([('%s:%s' % (k, str(v).replace('.', '_')), v) for k, v in page.items()])
        item['data'] = data
        item.setItem('pages', PageListResolver(), cacheTime=2)
        return item
        
    def list_connections(self):
        connectionsDict = self._page.site.register_connection.connections()
        result = Bag()
        for connection_id, connection in connectionsDict.items():
            delta = (datetime.datetime.now() - connection['start_ts']).seconds
            user = connection['user'] or 'Anonymous'
            ip = connection['user_ip'].replace('.', '_')
            connection_name = connection['connection_name']
            user_agent = connection['user_agent']
            itemlabel = '%s.%s (%i)' % (user, connection_name, delta)
            resolver = ConnectionListResolver(connection_id)
            result.setItem(itemlabel, resolver, cacheTime=1, connection_id=connection_id)
        return result
        
class PageListResolver(BagResolver):
    classKwargs = {'cacheTime': 1,
                   'readOnly': False,
                   'pageId': None}
    classArgs = ['pageId']
    
    def load(self):
        if not self.pageId:
            return self.list_pages()
        else:
            return self.one_page()
            
    def one_page(self):
        register = self._page.site.register_page
        page = register.get_register_item(self.pageId)
        item = Bag()
        data = page.pop('data', None)
        item['info'] = Bag([('%s:%s' % (k, str(v).replace('.', '_')), v) for k, v in page.items()])
        item['data'] = data
        return item
        
    def list_pages(self):
        pagesDict = self._page.site.register_page.pages()
        result = Bag()
        for page_id, page in pagesDict.items():
            delta = (datetime.datetime.now() - page['start_ts']).seconds
            pagename = page['pagename'].replace('.py', '')
            user = page['user'] or 'Anonymous'
            ip = page['user_ip'].replace('.', '_')
            itemlabel = '%s (%s).%s (%i)' % (user, ip, pagename, delta)
            resolver = PageListResolver(page_id)
            result.setItem(itemlabel, resolver, cacheTime=1)
        return result
        