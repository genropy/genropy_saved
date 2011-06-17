#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public,foundation/includedview'

    def pageAuthTags(self, method=None, **kwargs):
        return ''

    def windowTitle(self):
        return '!!Pages'

    def struct_pages(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('pagename', name='Pagename', width='10em')
        r.cell('subscribed_tables', name='Subs. Tables', width='10em')
        r.cell('start_ts', name='Start Ts', width='10em')
        r.cell('connection_id', name='Conn id', width='10em')
        r.cell('object_id', name='Obj Id', width='10em')
        return struct

    def main(self, rootBC, **kwargs):
        mainbc, top, bottom = self.pbl_rootBorderContainer(rootBC, title='Served Pages')
        mainbc.dataRpc('info.served_pages', 'get_current_pages', _fired='^refresh', _timing='=timing')
        mainbc.dataRpc('info.filtered_served_pages', 'get_current_pages', idx='^sel_table')

        mainbc.dataRpc('info.subscribed_tables', 'get_subscribed_tables', _fired='^refresh', _timing='=timing')

        bottom['right'].button('Refresh', fire='refresh', float='right')
        bottom['right'].horizontalslider(value='^timing', width='150px',
                                         minimum=0, maximum=60, discreteValues=61, float='right')

        self.top(mainbc.borderContainer(region='top', height='50%', splitter=True, margin='5px', margin_bottom=0))
        self.center(mainbc.borderContainer(region='center', margin='5px'))

    def top(self, bc):
        self.includedViewBox(bc, storepath='info.served_pages', struct=self.struct_pages(), datamode='bag',
                             label='All Served Pages')

    def center(self, bc):
        def label(pane, **kwargs):
            lbl = pane.div('!!Pages for subscribed tables')
            pane.menu(storepath='info.subscribed_tables', action='SET sel_table=$1.label', modifiers='*')

        self.includedViewBox(bc, label=label, storepath='info.filtered_served_pages', datamode='bag',
                             struct=self.struct_pages(), autoWidth=True)


    def rpc_get_current_pages(self, idx=None):
        return Bag(self.site.register_page.pages(idx))

    def rpc_get_subscribed_tables(self):
        l = self.site.register_page.get_index(index_name='*')
        result = Bag()
        for i, elem in enumerate(l):
            print elem
            result.setItem('r_%i' % i, None, label=elem)
        print result
        return result