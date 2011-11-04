# -*- coding: UTF-8 -*-

"""slotButtons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_basic(self, pane):
        """slotButton, standard button"""
        fb = pane.formbuilder(cols=3)
        fb.slotButton('I\'m the label, but I work as a tooltip', iconClass="icnBuilding", action='alert("Hello!")',colspan=2)
        fb.div('This is the standard usage of a slotButton: the label works as a tooltip')
        fb.button('button + icon', iconClass="icnBuilding",
                   action='alert("fb.button(\'button + icon\', iconClass=\'icnBuilding\')")')
        fb.slotButton('slotButton + icon', showLabel=True, iconClass="icnBuilding",
                       action='alert("fb.slotButton(\'slotButton + icon\', showLabel=True, iconClass=\'icnBuilding\')")')
        fb.div('Here we have a button and a slotButton set equal (with the "iconClass" attribute)')
        fb.button('button', action='alert("fb.button(\'button\')")')
        fb.slotButton('slotButton', action='alert("fb.slotButton(\'slotButton\')")')
        fb.div('Here we have a button and a slotButton set equal (without the "iconclass" attribute)')