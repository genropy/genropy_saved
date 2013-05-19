# -*- coding: UTF-8 -*-

# bugsxml.py
# Created by Francesco Porcari on 2012-03-01.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
         
    def test_0_dataxml(self,pane):
        """First test description"""
        pane.dataController("""
        	var b = new gnr.GnrBag();
        	var c = new gnr.GnrBag();
        	c.setItem('zzz','aaa',{_pippo:null,paperino:3,papa:null})
        	b.setItem('ttt',c,{_pippo:null,paperion:22,papa:null})
        	genro.serverCall('bugkwargs',{data:b});
        """,_onStart=False)

    def test_1_xxx(self,pane):
        box = pane.div(datapath='piero')
        box.div(margin_left='15px',display='inline-block').radioButton('Pippo',value='^.pippo',group='aaa')
        box.div(margin_left='15px',display='inline-block').radioButton('Paperino',value='^.paperino',group='aaa')
        box.div(margin_left='15px',display='inline-block').radioButton('Pluto',value='^.pluto',group='aaa')

    @public_method
    def bugkwargs(self,data=None):
    	print x