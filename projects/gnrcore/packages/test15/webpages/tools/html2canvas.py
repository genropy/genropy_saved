# -*- coding: UTF-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """HTMLTOCANVAS"""
        bc = pane.borderContainer(height='500px')
        top = bc.contentPane(region='top',height='50px',background='lime')
        top.button('Test',action="""
            genro.dom.htmlToCanvas(dojo.body(),{uploadPath:p})
            """,d=bc.js_domNode,p=self.site.getStaticPath('site:testcanvas'))
        bc.contentPane(region='left',width='50px',background='red')
        bc.contentPane(region='center',background='pink')