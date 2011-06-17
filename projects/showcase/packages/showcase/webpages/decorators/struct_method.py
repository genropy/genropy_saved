# -*- coding: UTF-8 -*-

# struct_method.py
# Created by Filippo Astolfi on 2011-05-10.
# Copyright (c) 2010 Softwell. All rights reserved.

"""struct_method"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_nostruct(self, pane):
        """no struct"""
        self.pippo(pane,name='pluto')
        
    def pippo(self,pane,name):
        pane.div(name,background='#00D200',color='white',font_size='2em')
        
    def test_2_struct(self, pane):
        """struct basic"""
        pane.pippo(name='yeah',color='white')
        
    @struct_method
    def xx_pippo(self,pane,name,color): # the "xx" prefix allow to distinguish the "xx_pippo" method from the "pippo" method
        pane.div(name,background='teal',color=color,font_size='2em')