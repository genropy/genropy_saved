# -*- coding: UTF-8 -*-
# 
"""Registered item tester"""
import datetime
from gnr.core.gnrbag import Bag,BagResolver
class GnrCustomWebPage(object):

    py_requires="testhandler:TestHandlerFull,storetester:StoreTester"
    dojo_theme='claro'
    
    def test_1_registered_pages(self,pane):
        """On current page """
        box = pane.div(datapath='test1',height='500px',overflow='auto')
        box.button('Refresh',fire='.refresh_treestore')
        box.dataRpc('.curr_pages.pages','curr_pages',_fired='^.refresh_treestore',_onResult='FIRE .refresh_tree')
        box.tree(storepath='.curr_pages',_fired='^.refresh_tree')
                    
    def test_2_registered_catalog(self,pane):
        box = pane.div(height='100px',datapath='test2')
        box.button('Get catalog',fire='.get_catalog')
        box.dataRpc('.catalog','get_catalog',_fired='^.get_catalog')
        
    def rpc_get_catalog(self):
        register_catalog = self.site.register_page.get_index()
        print xx

        
    def rpc_curr_pages_old(self):
        pagesDict = self.site.register_page.pages()
        result = Bag()
        for page_id,v in pagesDict.items():
            user = v['user'] or v['user_ip'].replace('.','_')
            pagename= v['pagename'].replace('.py','')
            connection_id = v['connection_id']
            delta = (datetime.datetime.now()-v['start_ts']).seconds
            result.addItem('.'.join([user,'%s (%i)' %(pagename,delta)]),None,
                            connection_id=connection_id,
                            page_id=page_id,user_ip=v['user_ip'],
                            user_agent=v['user_agent'],
                            user=user,
                            start_ts=v['start_ts'],
                            last_ts=v['last_ts'])
        return result 
        
    def rpc_curr_pages(self):
        pagesDict = self.site.register_page.pages()
        result = Bag()
        for page_id,page in pagesDict.items():
           #item = Bag()
           #data = page.pop('data',None)
           #item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in page.items()])
           #item['data'] = data
            delta = (datetime.datetime.now()-page['start_ts']).seconds
            pagename= page['pagename'].replace('.py','')
            user = page['user'] or 'Anonymous'
            ip =  page['user_ip'].replace('.','_')
            itemlabel = '%s (%s).%s (%i)' %(user,ip,pagename,delta)
            resolver = PageListResolver(page_id)
            result.setItem(itemlabel,resolver,cacheTime=1)
         
        return result 

class PageListResolver(BagResolver):
    classKwargs={'cacheTime':1,
                 'readOnly':False,
                 'pageId':None}
    classArgs=['pageId']
    def load(self):
        register = self._page.site.register_page
        page = register.get_register_item(self.pageId)
        item = Bag()
        data = page.pop('data',None)
        item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in page.items()])
        item['data'] = data
        return item