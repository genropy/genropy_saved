# -*- coding: utf-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

"includedview: bagstore"
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from docker.client import Client

class GnrCustomWebPage(object):
    dojo_source = True
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_base(self,pane):
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.daemon_address',lbl='Daemon address')
        left = bc.contentPane(region='left',width='300px')
        left.quickGrid(value='^.images')
        left.dataRpc('.images',self.getImages,daemon_address='^.daemon_address')

    @public_method
    def getImages(self,daemon_address=None):
        c = Client(daemon_address)
        result = Bag()
        for i,image in enumerate(c.images()):
            result['r_%i' %i] = Bag(image)
        return result