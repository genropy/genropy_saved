# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method

class GnrCustomWebPage(object):
    js_requires='socket.io'
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.contentPane(region='top')
        fb = top.div(padding='10px').formbuilder(cols=2,border_spacing='3px')
        fb.textbox(value='^.alfa',lbl='Alfa')

        bc.contentPane(region='center')

