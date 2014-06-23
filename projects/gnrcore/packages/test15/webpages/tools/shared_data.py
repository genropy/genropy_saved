# -*- coding: UTF-8 -*-
# 
"""Shared data tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'

    def test_1_shared_data_set_get(self, pane):
        """1-Shared Data SET and GET"""
        fb = pane.formbuilder(cols=5, border_spacing='3px', fld_width='8em', datapath='test1')
        fb.textbox(value='^.item_key', lbl='Key')
        fb.textbox(value='^.item_value', lbl='Value')
        fb.button('Set value', fire='.set_item')
        fb.button('Get item', fire='.get_item')

        fb.dataRpc('dummy', 'setInShared', item_value='=.item_value',
                   item_key='=.item_key', _fired='^.set_item')
        fb.dataRpc('.item_remote', 'getFromShared',
                   item_key='=.item_key',
                   _fired='^.get_item')
        fb.textbox(value='^.item_remote', lbl='Read value')

    def rpc_setInShared(self, item_key=None, item_value=None):
        self.site.shared_data.set(item_key, item_value)
        return item_value

    def rpc_getFromShared(self, item_key=None):
        item_value = self.site.shared_data.get(item_key)
        return item_value