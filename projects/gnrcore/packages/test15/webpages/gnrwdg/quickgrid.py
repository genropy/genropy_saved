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
        frame = pane.framePane(frameCode='test',height='300px')
        frame.top.slotToolbar('*,delrow,addrow,2')
        frame.quickGrid(value='^.griddata',
                        frameTarget=True,
                        selfsubscribe_addrow='this.widget.addRows($1._counter,$1.evt)',
                        format=[dict(field='test',name='Test',width='20em',edit=True),
                                                  dict(field='foo',name='Foo',width='5',dtype='L',edit=True)])


    @public_method
    def getCpuTimes(self):
        return self.site.getService('sysinfo').getCpuTimes()
  