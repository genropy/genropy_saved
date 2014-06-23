#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    pageOptions = {'openMenu': False}
    auth_main = 'admin'

    def windowTitle(self):
        return '!!System Dashboard'

    def main(self, root, **kwargs):
        frame = root.rootContentPane(title='!!Connections',datapath='main')
        f = frame.framePane(frameCode='mainframe')
        sc = f.center.stackContainer()
        sc.dataRpc('data', self.update_data, _onStart=True,
                    user_logged='^.userframe.logged',
                    user_guest='^.userframe.guest',
                  _fired='^refresh_all')
        f.top.slotToolbar('*,stackButtons,*',height='22px')
        self.user_pane(sc.borderContainer(title='Overall',_anchor=True))
        sc.contentPane(title='Connections')
        sc.contentPane(title='Pages')

    def user_struct(self,struct):
        r = struct.view().rows()
        r.cell('user', width='18em', name='User')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')


    def connection_struct(self,struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='15em', name='Connection id')
        r.cell('user_ip', width='12em', name='User')
        r.cell('browser_name', width='10em', name='Browser')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_refresh_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')

    def user_pane(self,bc):
        left = bc.contentPane(region='left',width='50%')
        frame = left.bagGrid(frameCode='users',title='Users',storepath='data.users',
                    struct=self.user_struct,pbl_classes=True,
                    margin='2px',addrow=False,delrow=False,datapath='.userframe')
        frame.store.attributes.update(sortedBy='=.grid.sorted')
        bar = frame.top.bar.replaceSlots('#','#,fb')
        fb = bar.fb.formbuilder(cols=2,border_spacing='3px',field_html_label=True)
        fb.checkbox(value='^.logged',label='Logged',default_value=True)
        fb.checkbox(value='^.guest',label='Guest',default_value=True)

        center = bc.borderContainer(region='center')
        top = center.contentPane(region='top',height='50%')
        top.bagGrid(frameCode='connections',title='Connections',storepath='data.connections',
                    struct=self.connection_struct,pbl_classes=True,
                    margin='2px',addrow=False,delrow=False,datapath='.userframe')
        center = center.contentPane(region='center')


    @public_method
    def update_data(self, user_guest=None,user_logged=None,**kwargs):
        result = Bag()
        users = self.site.register.users()
        user_keys = users.keys()
        if not user_logged:
            [users.pop(k) for k in user_keys if not k.startswith('guest_')]
        if not user_guest:
            [users.pop(k) for k in user_keys if k.startswith('guest_')]
        result['users'] = self.get_items(users, 'connections')
        connections = self.site.register.connections()
        result['connections'] = self.get_items(connections, 'pages')
        pages = self.site.register.pages()
        result['pages'] = self.get_items(pages)
        return result

    def get_items(self, items, child_name=None, **kwargs):
        result = Bag()
        for key, item in items.items():

            _customClasses = []
            item['_pkey'] = key
            if item['last_refresh_age'] > 60:
                _customClasses.append('disconnected')
            elif item['last_event_age'] > 60:
                _customClasses.append('inactive')
            if child_name and not item[child_name]:
                _customClasses.append('no_children')
            item.pop('datachanges', None)
            result.setItem(key, Bag(item), _customClasses=' '.join(_customClasses))
        return result
