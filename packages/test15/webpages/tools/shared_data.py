# -*- coding: UTF-8 -*-
# 
"""Shared data tester"""

class GnrCustomWebPage(object):

    py_requires="testhandler:TestHandlerBase"
    dojo_theme='claro'
    
    def test_1_shared_data_set_get(self,pane):
        """1-Shared Data SET and GET"""
        fb = pane.formbuilder(cols=5, border_spacing='3px',fld_width='8em')
        fb.textbox(value='^item_key',lbl='Key')
        fb.textbox(value='^item_value',lbl='Value')
        fb.button('Set value',fire='set_item')
        fb.button('Get item',fire='get_item')
        
        pane.dataRpc('dummy','setInShared',item_value='=item_value',
                    item_key='=item_key',_fired='^set_item',
                    _onResult='alert("set")')
        pane.dataRpc('item_remote','getFromShared',
                    item_key='=item_key',
                    _fired='^get_item')
        fb.numberTextBox(value='^item_remote',lbl='Read value')
    
    def test_2_shared_data_increment(self,pane):
        """2-Shared Data Incr"""
        fb = pane.formbuilder(cols=5, border_spacing='3px',fld_width='8em')
        fb.textbox(value='^item_key',lbl='Key')
        fb.textbox(value='^delta',default_value=1,lbl='Delta')
        fb.button('Increment value',fire='increment_value')
        fb.button('Get item',fire='get_item')
        fb.textbox(value='^item_remote',lbl='New value')
        pane.dataRpc('dummy','incrementSharedItem',
                    item_key='=item_key',delta='=delta',
                    _fired='^increment_value')

        
    def rpc_setInShared(self,item_key=None,item_value=None):
        self.site.shared_data.set(item_key,item_value)
        return item_value
        
    def rpc_getFromShared(self,item_key=None):
        item_value = self.site.shared_data.get(item_key)
        return item_value
        
    def rpc_incrementSharedItem(self,item_key=None,delta=None):
        self.site.shared_data.incr(item_key,delta)