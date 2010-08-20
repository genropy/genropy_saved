# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test Messages"""
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    dojo_theme='tundra'
    py_requires="testhandler:TestHandlerFull,storetester:StoreTester"

    def windowTitle(self):
        return 'test msg'
         
    def test_1_simplemessage(self,pane):
        "Page Message"
        self.common_pagemenu(pane.div(datapath='test_1',height='80px'))
        fb = pane.formbuilder(cols=4, border_spacing='3px',datapath='test_1')
        fb.textbox(value='^.page_msg')
        fb.button('Send',fire='.send_page_message')
        fb.dataRpc('dummy','sendPageMsg',msg='=.page_msg',pageId='=.pageId',_fired='^.send_page_message')
        fb.div('^.test')
        
    def rpc_sendPageMsg(self,msg=None,pageId=None):
        body = Bag()
        pageId= pageId or self.page_id
        body.setItem('test',msg,_client_data_path='test_1.test')
        print 'before writeMessage'
        self.site.writeMessage(body=body,page_id=pageId,message_type='datachange')
        print 'after writeMessage'

    
    def test_2_setInClientData(self,pane):
        """Set in client data"""
        center = self.common_pages_container(pane,height='350px',background='whitesmoke',
                                            datapath='test_2')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.div('^.pageId',lbl='Selected page')
        fb.textbox(value='^.clientdata_address',lbl='Address')
        fb.textbox(value='^.clientdata_value',lbl='Value')
        fb.button('Send',fire='.clientdata_set')
        fb.dataRpc('dummy','setInClientData',value='=.clientdata_value',page='=.pageId',
                    address='=.clientdata_address',_fired='^.clientdata_set')
            
    def rpc_setInClientData(self,page=None,address=None,value=None):
        body = Bag()
        body.setItem('x',value,_client_data_path=address)
        self.site.writeMessage(body=body,page_id=page,message_type='datachange')


        