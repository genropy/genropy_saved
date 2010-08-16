# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    dojo_theme='claro'
    py_requires="testhandler:TestHandlerBase"

    def windowTitle(self):
        return 'test msg'
         
    def test_1_page_message(self,pane):
        "Page Message"
        fb = pane.formbuilder(cols=4, border_spacing='3px')
        fb.textbox(value='^page_msg')
        fb.button('Send',fire='send_page_message')
        pane.dataRpc('dummy','sendPageMsg',msg='=page_msg',_fired='^send_page_message')
        
        fb.button('Ping',action='genro.ping();')
        fb.div('^test')

    def rpc_sendPageMsg(self,msg=None):
        print self.site.page_register.pages()
        body = Bag()
        body.setItem('test',msg,_client_data_path='test')
        self.site.writeMessage(body=body,page_id=self.page_id,message_type='datachange')
        