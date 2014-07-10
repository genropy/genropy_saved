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
    def test_1_format_editable(self,pane):
        t = pane.table().tbody()
        r = t.tr()
        self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='TL')
        self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='TR')
        r = t.tr()
        self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='BL')
        self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='BR')


    def quickGridEditable(self,pane,pos=None):
        box = pane.div(datapath='.%s' %pos)
        b = Bag()
        pane.data('.griddata',b)
        box.formbuilder().textBox('^.def_location',lbl='Default location')
        format=[dict(field='name',name='Name',width='20em',edit=True),
                dict(field='location',name='Location',width='5em',edit=True)]
        box.quickGrid(value='^.griddata',
                        format=format,default_location='=.def_location',
                        tools='addrow,delrow,duprow,export',
                        tools_position=pos,height='150px',width='400px' ,border='1px solid silver'
                        )
                        
    def _test_2_syntax(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px')
        grid=bc.contentPane(region='center').quickGrid(value='^.data.rows')
        grid.column('name',name='Name',width='10px')
        grid.column('age',name='Age',width='10px')
        gridtop=grid.top(height='20px').slotToolbar('*,addrow,delrow,2')
        gridbottom=grid.bottom(height='20px')
        
    def _test_3_framepane_syntax(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px')
        pane=bc.framePane(region='center')
        ptop=pane.top(height='20px').slotToolbar('*,foo,egg,2')
        ptop.foo.div('pppppp')
        ptop.egg.div('pppppp')
        pbottom=pane.bottom(height='20px')
   



    @public_method
    def getCpuTimes(self):
        return self.site.getService('sysinfo').getCpuTimes()
  