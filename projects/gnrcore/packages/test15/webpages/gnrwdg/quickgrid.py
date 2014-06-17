# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag
from gnr.core.decorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    css_requires='public'
    
    def windowTitle(self):
        return 'bageditor'
         
    def test_0_firsttest(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px')
        bc.dataRpc('.data.rows',self.getCpuTimes,_timer=10)
        bc.contentPane(region='center').quickGrid(value='^.data.rows')
    

    @public_method
    def getCpuTimes(self):
        return self.site.getService('sysinfo').getCpuTimes()
 