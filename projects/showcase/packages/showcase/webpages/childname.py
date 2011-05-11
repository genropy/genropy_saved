# -*- coding: UTF-8 -*-

# childname.py
# Created by Filippo Astolfi on 2011-05-10.
# Copyright (c) 2010 Softwell. All rights reserved.

"""childname"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_childname(self, pane):
        """childname with struct"""
        pippo = pane.pippo()
        pippo.red.span('hello')
        pippo.lime.button('click me', action='alert("hello!")')
        pippo.bottone
        pippo.bottone.div('36')
        
    @struct_method
    def xx_pippo(self,pane):
        box = pane.div(background='teal')
        box.div(childname='red',background='red',height='25px')
        box.div(childname='lime',background='lime',height='40px')
        box.button('ciao',childname='bottone',action='alert("ho capito!")')
        return box