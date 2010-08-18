# -*- coding: UTF-8 -*-
# 
"""ServerStore tester"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):

    py_requires="testhandler:TestHandlerBase"
    dojo_theme='claro'
    
    def test_1_current_page(self,pane):
        """On current page """
        self.common_form(pane,datapath='test_1')
                    
    def test_2_external_page(self,pane):
        """Set in external store"""
        center = self.common_pages_container(pane,height='350px',background='whitesmoke',
                                            datapath='test_2')
        self.common_form(center)

    def common_form(self,pane,datapath=None):
        fb = pane.formbuilder(cols=2, border_spacing='3px',fld_width='8em',datapath=datapath)
        fb.textbox(value='^.item_key',lbl='Key')
        fb.br()
        fb.numberTextBox(value='^.item_value_w',lbl='Value to write')
        fb.button('Set value',fire='.set_item')
        fb.numberTextBox(value='^.item_value_r',lbl='Value in store')
        fb.button('Get item',fire='.get_item')
        fb.dataRpc('dummy','serverStoreSet',item_value='=.item_value_w',
                    item_key='=.item_key',_fired='^.set_item',pageId='=.pageId')
                    
        fb.dataRpc('.item_value_r','serverStoreGet',
                    item_key='=.item_key',
                    _fired='^.get_item',pageId='=.pageId')
                    
    def common_tree(self,pane):
        bc = pane.borderContainer()
        top = bc.contentPane(region='top')
        bottom= bc.contentPane(region='bottom',background='yellow')
        center = bc.contentPane(region='center')
        top.button('Refresh',fire='.refresh_currpages')
        center.tree(storepath='.root',_fired='^.endrpc',selected_page_id='.pageId',
                    selected_start_ts='.start_ts',
                    selected_user_agent='.user_agent',
                    selected_user='.user',
                    selected_connection_id='.connection_id',
                    selected_user_ip='.user_ip',
                    inspect='*',hideValues=True)
        fb = bottom.formbuilder(cols=1, border_spacing='2px',font_size='7px')
        fb.div('^.page_id',lbl='Page')
        fb.div('^.connection_id',lbl='Connection_id')
        fb.div('^.user',lbl='User')
        fb.div('^.user_ip',lbl='User ip')
        fb.div('^.user_agent',lbl='User agent')
        fb.div('^.start_ts',lbl='Start ts')
        pane.data('.root.pages',Bag())
        pane.dataRpc('.root.pages','curr_pages',_fired='^.refresh_currpages',_onResult='FIRE .endrpc;')
    
    def common_pages_container(self,pane,**kwargs):
        bc = pane.borderContainer(**kwargs)
        left = bc.contentPane(region='left',width='240px',splitter=True)
        right = bc.contentPane(region='right',width='240px',splitter=True)
        self.store_tree(right)

        self.common_tree(left)
        return bc.contentPane(region='center')
    
    def store_tree(self,pane):
        pane.tree(storepath='.store',_fired='^.rebuld_store_tree')
        pane.data('.store.current',Bag())
        pane.dataRpc('.store.current','currentStore',pageId='^.pageId',_onResult='FIRE .rebuld_store_tree')
        
    def rpc_currentStore(self,pageId=None):
        store = self.get_store(pageId)
        store.load()
        return store.data
        
    def rpc_serverStoreSet(self,item_key=None,item_value=None,pageId=None):
        store = self.get_store(pageId)
        store.load(lock=True)
        store.setItem(item_key,item_value)
        store.save(unlock=True)
        
    def rpc_serverStoreGet(self,item_key=None,pageId=None):
        store = self.get_store(pageId)
        item_value = store.getItem(item_key)
        return item_value
        
    def rpc_curr_pages(self):
        pagesDict = self.site.page_register.pages()
        result = Bag()
        for page_id,v in pagesDict.items():
            user = v['user'] or 'Anonymous'
            pagename= v['pagename'].replace('.py','')
            connection_id = v['connection_id']
            result.addItem('.'.join([user,pagename]),None,
                            connection_id=connection_id,
                            page_id=page_id,user_ip=v['user_ip'],
                            user_agent=v['user_agent'],
                            user=user,
                            start_ts=v['start_ts'])
        return result 