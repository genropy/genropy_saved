# -*- coding: UTF-8 -*-
# 
"""Registered connections tester"""
import datetime
from gnr.core.gnrbag import Bag,BagResolver
class GnrCustomWebPage(object):

    py_requires="testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme='claro'
    
    def test_1_registered_connections(self,pane):
        """Connections tree"""
        box = pane.div(datapath='test1',height='500px',overflow='auto')
        box.button('Refresh',fire='.refresh_treestore')
        box.dataRpc('.connections','curr_connections',_fired='^.refresh_treestore',_onResult='FIRE .refresh_tree')
        box.tree(storepath='.connections',_fired='^.refresh_tree')

    def rpc_curr_connections(self):
        connectionsDict = self.site.register_connection.connections()
        result = Bag()
        for connection_id,connection in connectionsDict.items():
            delta = (datetime.datetime.now()-connection['start_ts']).seconds
            user = connection['user'] or 'Anonymous'
            ip =  connection['user_ip'].replace('.','_')
            connection_name=connection['connection_name']
            user_agent=connection['user_agent']
            itemlabel = '%s.%s (%i)' %(user,connection_name,delta)
            resolver = ConnectionListResolver(connection_id)
            result.setItem(itemlabel,resolver,cacheTime=1)
        return result 

class ConnectionListResolver(BagResolver):
    classKwargs={'cacheTime':1,
                 'readOnly':False,
                 'connectionId':None}
    classArgs=['connectionId']
    def load(self):
        register = self._page.site.register_connection
        page = register.get_register_item(self.connectionId)
        item = Bag()
        data = page.pop('data',None)
        item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in page.items()])
        item['data'] = data
        return item