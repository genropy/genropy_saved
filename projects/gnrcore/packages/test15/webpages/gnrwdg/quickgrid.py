# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    css_requires='public'
    

    def test_0_firsttest(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px')
        bc.dataRpc('.data.rows',self.getCpuTimes,_timer=10)
        bc.contentPane(region='center').quickGrid(value='^.data.rows')
   
    def test_1_format_editable(self,pane):
        b = Bag()
        pane.data('.griddata',b)
        format=[dict(field='test',name='Test',width='20em',edit=True),
                                dict(field='foo',name='Foo',width='5',dtype='L',edit=True)]
        pane.div(height='50px',background='white')
        grid = pane.quickGrid(value='^.griddata',
                        format=format,defualt_test='=pierino',
                        tools='addrow,delrow:TR',height='300px')




    @public_method
    def getCpuTimes(self):
        return self.site.getService('sysinfo').getCpuTimes()
  