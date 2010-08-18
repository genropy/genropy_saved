# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test Messages"""
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    dojo_theme='tundra'
    py_requires="testhandler:TestHandlerFull"

    def windowTitle(self):
        return 'test msg'
         
    def test_1_simplemessage(self,pane):
        "Page Message"
        fb = pane.formbuilder(cols=4, border_spacing='3px')
        fb.textbox(value='^page_msg')
        fb.button('Send',fire='send_page_message')
        pane.dataRpc('dummy','sendPageMsg',msg='=page_msg',_fired='^send_page_message')
        
        fb.button('Ping',action='genro.ping();')
        fb.div('^test')
    
    def test_2_setInClientData(self,pane):
        """Set in client data"""
        bc = pane.borderContainer(height='300px',background='whitesmoke')
        left = bc.contentPane(region='left',width='150px',splitter=True)
        left.button('Refresh',fire='refresh_currpages')
        left.tree(storepath='root',_fired='^endrpc',selected_page_id='selected_page')
        left.data('root.pages',Bag())
        left.dataRpc('root.pages','currPages',_fired='^refresh_currpages',_onResult='FIRE endrpc;')
        
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.div('^selected_page',lbl='Selected page')
        fb.textbox(value='^clientdata_address',lbl='Address')
        fb.textbox(value='^clientdata_value',lbl='Value')
        fb.button('Send',fire='clientdata_set')
        fb.dataRpc('dummy','setInClientData',value='=clientdata_value',page='=selected_page',
                    address='=clientdata_address',_fired='^clientdata_set')
            
    def rpc_setInClientData(self,page=None,address=None,value=None):
        body = Bag()
        body.setItem('x',value,_client_data_path=address)
        self.site.writeMessage(body=body,page_id=page,message_type='datachange')

    def rpc_currPages(self):
        pagesDict = self.site.page_register.pages()
        result = Bag()
        for page_id,v in pagesDict.items():
            user = v['user'] or 'Anonymous'
            pagename= v['pagename'].replace('.py','')
            connection_id = v['connection_id']
            result.setItem('.'.join([user,'%s (%s)' %(pagename,page_id)]),page_id,connection_id=connection_id,page_id=page_id)
        return result 
        
    def rpc_sendPageMsg(self,msg=None):
        body = Bag()
        body.setItem('test',msg,_client_data_path='test')
        self.site.writeMessage(body=body,page_id=self.page_id,message_type='datachange')
        