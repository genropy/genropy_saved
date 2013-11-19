# -*- coding: UTF-8 -*-

# messages.py
# Created by Francesco Porcari on 2010-08-26.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Messages"""

from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwsgisite_proxy.gnrsiteregister import RegisterResolver
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'Messages'

    def test_2_sitereg(self,pane):
        bc = pane.borderContainer(height='800px')
        fb = bc.contentPane(region='top').formbuilder(cols=4,border_spacing='3px')
        fb.button('Sbang',fire='.error')
        fb.dataRpc('.members',self.errormaker,_fired='^.error')

    @public_method
    def errormaker(self):
        item = self.site.register.newregister.get_item(self.page_id,'lazy',register_name='page')
        item['data'].setItem('pippo',33)
        print x