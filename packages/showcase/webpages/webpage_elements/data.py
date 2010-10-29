# -*- coding: UTF-8 -*-

# data.py
# Created by Filippo Astolfi on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""data"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """data basic example - button attributes"""
        bc = pane.borderContainer(datapath='test1')
        bc.data('.icon','icnBaseOk')
        bc.data('.fontType','Courier')
        bc.data('.widthButton','10em')
        bc.data('.fontSize','22px')
        bc.data('.color','green')
        bc.button('Click me',iconClass='^.icon',width='^.widthButton',color='^.color',
                   font_size='^.fontSize',font_family='^.fontType',action="alert('Clicked!')")
                   
    def test_2_basic2(self,pane):
        """data basic example - formbuilder attributes"""
        bc = pane.borderContainer(datapath='test2')
        fb = bc.formbuilder(cols=2)
        fb.data('.name','Filippo')
        fb.data('.surname','Astolfi')
        fb.textbox(value='^.name',lbl='!!Name')
        fb.textbox(value='^.surname',lbl='!!Surname')
        fb.numberTextbox(value='^.phone',lbl='!!Phone number')
        fb.textbox(value='^.address',lbl='!!Address')