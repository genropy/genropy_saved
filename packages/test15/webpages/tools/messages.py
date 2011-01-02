# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-26.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,storetester:StoreTester"

    def windowTitle(self):
        return 'Messages'

    def test_1_send_message(self, pane):
        center = self.common_pages_container(pane, datapath='test1', height='400px')
        fb = center.formbuilder(cols=1, border_spacing='4px')
        fb.textbox(value='^.message', lbl='Message')
        fb.textbox(value='^.info.pageId', lbl='Page Id')
        fb.textbox(value='^.filters', width='40em', lbl='Filters')
        fb.button('Send', fire='.send_message')
        center.dataRpc('dummy', 'sendMessageToClient', _fired='^.send_message',
                       message='=.message', pageId='=.info.pageId', filters='=.filters')
            