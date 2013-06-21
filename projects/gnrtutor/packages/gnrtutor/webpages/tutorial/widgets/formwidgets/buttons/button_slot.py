# -*- coding: UTF-8 -*-


"""Slot Button Example"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height='200',description='Slot Button')
    def slotbutton(self,pane):
        fb = pane.formbuilder(cols=3)
        fb.slotButton('I\'m the label, but I work as a tooltip', 
                      iconClass="icnBuilding", 
                      action='alert("I am a slotbutton")',colspan=2)

    def doc_slotbutton(self):
        """This is the standard usage of a slotButton: the label works as a tooltip. 
"""


    @example(code=2,height='400',description='More Slot Buttons and comparision with simple buttons.')
    def slotbutton2(self, pane):

        action = 'alert("you clicked me")'
        iconclass = 'iconbox info'

        fb = pane.formbuilder(cols=4)

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
        fb.div('This is a WRONG way to build a slotButton: instead use a standard button example n.1')

        fb.div('6)')
        fb.button('click', iconClass=iconclass, showLabel=False, action=action)
        fb.div('[iconClass: iconbox info; showLabel: False]')
        fb.div('This is the way to set a button with the features of a basic slotButton (like the example n.3)')

    def doc_slotbutton2(self):
        """In this example every button (and slotButton) has the \"label\" attribute set to \"click\";
In addition, every button (and every slotButton) has the following \"action\" attribute: <I>action = alert("you clicked me")</I>

The slotButton and button widgets are very similar. Generally speaking you should use the slotButton for icon buttons.
The example shows some alternatives in creating the same effect, and some syntax to avoid.
"""