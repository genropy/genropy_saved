# -*- coding: UTF-8 -*-
"""slotButtons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_basic(self, pane):
        """slotButton, standard button"""
        fb = pane.formbuilder(cols=3)
        fb.slotButton('I\'m the label, but I work as a tooltip', iconClass="icnBuilding", action='alert("Hello!")',colspan=2)
        fb.div('This is the standard usage of a slotButton: the label works as a tooltip')
        
    def test_2_buttons(self, pane):
        """simple button and slotButton"""
        action = 'alert("you clicked me")'
        iconclass = 'iconbox info'
        
        fb = pane.formbuilder(cols=4)
        fb.div('In this example every button (and slotButton) has the \"label\" attribute set to \"click\";', colspan=4)
        fb.div("""also, every button (and every slotButton) has the following \"action\" attribute:
                  action = alert("you clicked me")""", colspan=4)
        
        fb.div('N.', font_size='1.2em', font_weight='bold')
        fb.div('widget', font_size='1.2em', font_weight='bold')
        fb.div('attributes', font_size='1.2em', font_weight='bold')
        fb.div('comment', font_size='1.2em', font_weight='bold')
        
        fb.div('1)')
        fb.button('click', action=action)
        fb.div('[No attributes]')
        fb.div('Standard way to build an iconless button')
        
        fb.div('2)')
        fb.button('click', iconClass=iconclass, action=action)
        fb.div('[iconClass: iconbox info]')
        fb.div('Standard way to build an icon button')
        
        fb.div('3)')
        fb.slotButton('click', iconClass=iconclass, action=action)
        fb.div('[iconClass: iconbox info]')
        fb.div('Standard way to build a slotButton')
        
        fb.div('4)')
        fb.slotButton('click', showLabel=True, iconClass=iconclass, action=action)
        fb.div('[showLabel=True; iconClass: iconbox info]')
        fb.div('Unusual way to build a slotButton: you can use the button of the example n.2')
        
        fb.div('5)')
        fb.slotButton('click', action=action)
        fb.div('[No attributes]')
        fb.div('This is a WRONG way to build a slotButton: if you need something like this, use the button of the example n.1')
        
        fb.div('6)')
        fb.button('click', iconClass=iconclass, showLabel=False, action=action)
        fb.div('[iconClass: iconbox info; showLabel: False]')
        fb.div('This is the way to set a button with the features of a basic slotButton (like the example n.3)')
        