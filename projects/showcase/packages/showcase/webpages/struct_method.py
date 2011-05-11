# -*- coding: UTF-8 -*-

# struct_method.py
# Created by Filippo Astolfi on 2011-05-10.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method

"""struct_method"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_nostruct(self, pane):
        """no struct"""
        self.pippo(pane,name='pluto')
        
    def pippo(self,pane,name):
        pane.div(name,background='pink')
        
    def test_2_struct(self, pane):
        """struct basic"""
        pane.pippo(name='yeah36')
        
    @struct_method
    def xx_pippo(self,pane,name): # l'xx davanti serve perché se no scazzerebbe perché c'è un altro metodo che si chiama pippo
        pane.div(name,background='teal')