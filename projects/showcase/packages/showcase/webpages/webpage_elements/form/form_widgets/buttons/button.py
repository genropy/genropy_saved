# -*- coding: UTF-8 -*-

# button.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Button"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def test_0_action(self,pane):
        """Action attribute"""
        fb = pane.formbuilder(cols=2)
        fb.div('The action attribute allow to write javascript code.',
                font_size='.9em',text_align='justify',colspan=2)
        fb.button('Button',action="alert('Hello!')",tooltip='click me!')
        fb.div("""Create an alert message through "action" attribute.
                  There is a tooltip, too.""",
                font_size='.9em',text_align='justify')
        fb.button('Confirm', action='confirm("Sure?")')
        fb.div('Create a confirm message through "action" attribute.',
                font_size='.9em',text_align='justify')
        fb.button('Resolution', action="SET .res = screen.width+' x '+screen.height;")
        fb.textbox(lbl='screen res',value='^.res',width='6em')
        
    def test_1_button(self,pane):
        """Button and Textbox"""
        pane.div("""This button will launch an alert message with the textbox content.
                 """,font_size='.9em',text_align='justify')
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.button('Alert message',iconClass="icnBaseOk",action='alert(textbox)',
                   textbox='^.tbValue')
        fb.textBox(value='^.tbValue')
        fb.data('.tbValue','Hello')
        
    def test_2_fire(self,pane):
        """FIRE attribute"""
        bc = pane.borderContainer(datapath='test2')
        bc.div("""There are three way to use FIRE:""",
                font_size='.9em',text_align='justify')
        bc.dataController('''alert(msg);''', msg='^.msg')
        fb = bc.formbuilder(cols=2)
        
        fb.button('Click me!',action="FIRE .msg='Click';")
        fb.div(""" "action="FIRE msg='Click';" [shows an alert message reporting "Click"] """,font_size='.9em')
        
        fb.button('Click me!',fire_Click = '.msg')
        fb.div(""" "fire_Click = 'msg'" [same result of the previous one]""",font_size='.9em')
        
        fb.button('Click me!',fire='.msg')
        fb.div(""" "fire='msg'" [shows an alert message reporting "true"] """,font_size='.9em')
        
    def test_3_graphical_attributes(self,pane):
        """Graphical attributes"""
        bc = pane.borderContainer(datapath='test3')
        bc.div(""" You can also change appearance of your button, with Dojo and CSS button attributes.""",
                font_size='.9em',text_align='justify')
        bc.data('.icon','icnBaseOk')
        bc.data('.fontType','Courier')
        bc.data('.widthButton','10em')
        bc.data('.fontSize','22px')
        bc.data('.color','green')
        bc.button('Click me',iconClass='^.icon',width='^.widthButton',color='^.color',
                    font_size='^.fontSize',font_family='^.fontType',action="alert('Clicked!')")
        
    def test_4_hidden(self,pane):
        """Hidden attribute"""
        bc = pane.borderContainer(height='100px',datapath='test4')
        bc.data('.hidden',False,_init=True)
        bc.dataController("""SET .hidden=true""",_fired='^.invisibility')
        bc.dataController("""SET .hidden=false""",_fired='^.show')
        fb = bc.formbuilder(cols=2)
        fb.button('Hide the div!',fire='^.invisibility')
        fb.button('Show the div!',fire='^.show')
        fb.div('You can hide me!',hidden='^.hidden',colspan=2,border='4px solid red')
                    