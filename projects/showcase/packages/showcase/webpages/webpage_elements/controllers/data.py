# -*- coding: UTF-8 -*-

# data.py
# Created by Filippo Astolfi on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""data"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """data basic example - button attributes"""
        pane.div('To assign a default value (like a string, a number, etc) you can use the data.',
                  margin='1em',font_width='0.9em')
        pane.div("""We remember you that the first parameter of the ``data`` controller specifies the path
        of the value of your object (so, it must coincide with the path of the object on which
        you want to set the default value), while the second parameter is the default you want
        to set.""",margin='1em',font_width='0.9em')
        bc = pane.borderContainer(datapath='test1')
        bc.data('.icon', 'icnBaseOk')
        bc.data('.fontType', 'Courier')
        bc.data('.widthButton', '10em')
        bc.data('.fontSize', '22px')
        bc.data('.color', 'green')
        bc.button('Click me',iconClass='^.icon',width='^.widthButton',color='^.color',
                  font_size='^.fontSize',font_family='^.fontType',action="alert('Clicked!')")

    def test_2_basic2(self, pane):
        """data basic example - filling some formbuilder attributes"""
        bc = pane.borderContainer(datapath='test2')
        fb = bc.formbuilder(cols=2)
        fb.data('.name', 'Philip')
        fb.data('.surname', 'Smith')
        fb.data('.phone','555-1230-0000')
        fb.textbox(value='^.name', lbl='!!Name')
        fb.textbox(value='^.surname', lbl='!!Surname')
        fb.textbox(value='^.phone', lbl='!!Phone number')
        fb.textbox(value='^.address', lbl='!!Address', ghost='1th avenue...')