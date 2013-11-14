# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-09.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
import datetime

class StoreTester(BaseComponent):
    def common_form(self, pane, datapath=None, common_rpc=True):
        fb = pane.formbuilder(cols=2, border_spacing='3px', fld_width='8em', datapath=datapath)
        fb.textbox(value='^.item_key', lbl='Key')
        fb.br()
        fb.textBox(value='^.item_value_w', lbl='Value to write')
        fb.button('Set value', fire='.set_item')
        fb.textBox(value='^.item_value_r', lbl='Value in store')
        fb.button('Get item', fire='.get_item')
        if common_rpc:
            fb.dataRpc('dummy', 'serverStoreSet', item_value='=.item_value_w',
                       item_key='=.item_key', _fired='^.set_item', pageId='=.info.pageId')

            fb.dataRpc('.item_value_r', 'serverStoreGet',
                       item_key='=.item_key',
                       _fired='^.get_item', pageId='=.info.pageId')


    def common_pagemenu(self, pane):
        
        pane.dropdownbutton('Page', float='left').menu(storepath='.pagemenu', selected_page_id='.info.pageId',
                                                       selected_start_ts='.info.start_ts',
                                                       selected_user_agent='.info.user_agent',
                                                       selected_user='.info.user',
                                                       selected_connection_id='.info.connection_id',
                                                       selected_user_ip='.info.user_ip')
        fb = pane.formbuilder(cols=1, border_spacing='2px', font_size='8px',
                              background='lightyellow', float='right')
        fb.div('^.info.pageId', lbl='Page')
        fb.div('^.info.connection_id', lbl='Connection_id')
        fb.div('^.info.user', lbl='User')
        fb.div('^.info.user_ip', lbl='User ip')
        fb.div('^.info.user_agent', lbl='User agent', width='200px')
        fb.div('^.info.start_ts', lbl='Start ts')
        pane.button('Current Page', action='SET info=null; FIRE .refresh_store;')
        pane.dataRemote('.pagemenu.pages', 'curr_pages', cacheTime=1)

    def common_pages_container(self, pane, **kwargs):
        bc = pane.borderContainer(**kwargs)
        left = bc.contentPane(region='top', height='80px', splitter=True)
        right = bc.contentPane(region='right', width='240px', splitter=True)
        self.common_current_store(right)
        self.common_pagemenu(left)
        return bc.contentPane(region='center')

    def common_current_store(self, pane):
        pane.button('Update', fire='.refresh_store')
        box = pane.div(height='200px')
        box.tree(storepath='.store', _fired='^.rebuld_store_tree', persist=True)
        box.data('.store.current', Bag())
        box.dataRpc('.store.current', 'currentRegister', pageId='^.info.pageId',
                    _onResult='FIRE .rebuld_store_tree', _fired='^.refresh_store')

    def rpc_currentRegister(self, pageId=None):
        store = self.pageStore(pageId)
        result = Bag()
        register_item = store.register_item
        result['data'] = store.data
        result['info'] = Bag(dict(user=register_item['user'], pageId=register_item['register_item_id'],
                                  start_ts=register_item['start_ts'], user_ip=register_item['user_ip'],
                                  user_agent=register_item['user_agent'], pagename=register_item['pagename']))
        return result

    def rpc_serverStoreSet(self, item_key=None, item_value=None, pageId=None):
        self.pageStore(pageId).setItem(item_key, item_value)

    def rpc_serverStoreGet(self, item_key=None, pageId=None):
        store = self.pageStore(pageId)
        item_value = store.getItem(item_key)
        return item_value

    def rpc_curr_pages(self):
        pagesDict = self.site.register_page.pages()
        result = Bag()
        for page_id, v in pagesDict.items():
            user = v['user'] or v['user_ip'].replace('.', '_')
            pagename = v['pagename'].replace('.py', '')
            connection_id = v['connection_id']
            delta = (datetime.datetime.now() - v['start_ts']).seconds
            result.addItem('.'.join([user, '%s (%i)' % (pagename, delta)]), None,
                           connection_id=connection_id,
                           page_id=page_id, user_ip=v['user_ip'],
                           user_agent=v['user_agent'],
                           user=user,
                           start_ts=v['start_ts'])
        return result 