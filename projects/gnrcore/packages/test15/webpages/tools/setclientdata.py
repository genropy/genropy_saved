# -*- coding: UTF-8 -*-

# serverpath.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Serverpath"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    auto_polling = 10
    user_polling = 3

    def test_0_setting(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.page_id',lbl='Page id')
        fb.textbox(value='^.path',lbl='Path')
        fb.textbox(value='^.value',lbl='Value')
        fb.textbox(value='^.dtype',lbl='Dtype')
        fb.checkbox(value='^.fired',lbl='Fired')

        fb.button('Send',fire='.send')
        fb.dataRpc('dummy',self.sendToOtherPage,dest_page_id='=.page_id',
                    dest_pagepath='=.path',dest_value='=.value',dest_dtype='=.dtype',
                    dest_fired='=.fired',_fired='^.send')

    @public_method
    def sendToOtherPage(self,dest_value=None, dest_pagepath=None,dest_attributes=None, dest_page_id=None, dest_filters=None,
                        dest_fired=False, dest_reason=None, dest_public=False, dest_replace=False,dest_dtype=None):

        if dest_dtype:
            dest_value = self.catalog.fromText(dest_value,dest_dtype)
        self.setInClientData(dest_pagepath,value=dest_value,page_id=dest_page_id,filters=dest_filters,fired=dest_fired,reason=dest_reason)


    def test_1_publishing(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.page_id',lbl='Page id')
        fb.textbox(value='^.topic',lbl='Topic')
        fb.textbox(value='^.nodeId',lbl='NodeId')
        fb.textbox(value='^.message',lbl='Message')
        fb.textbox(value='^.messageType',lbl='Level')

        fb.button('Send',fire='.send')
        fb.dataRpc('dummy',self.publishToOtherPage,dest_page_id='=.page_id',
                    dest_topic='=.topic',dest_nodeId='=.nodeId',dest_message='=.message',
                    dest_messageType='=.messageType',_fired='^.send')

    @public_method
    def publishToOtherPage(self,dest_topic=None,dest_page_id=None, dest_nodeId=None,dest_message=None,dest_messageType=None):
        self.clientPublish(topic=dest_topic,nodeId=dest_nodeId,page_id=dest_page_id,message=dest_message,messageType=dest_messageType)
