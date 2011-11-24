# -*- coding: UTF-8 -*-
"""macros"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def test_1_fire(self,pane):
        """macro (FIRE)"""
        bc = pane.borderContainer()
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
        
    def test_2_set(self,pane):
        """macro (SET)"""
        pane.data('.number', 0)
        pane.dataController("""SET .number=36;""",_fired='^.my_button')
        bc = pane.borderContainer()
        fb = bc.formbuilder(cols=2)
        fb.div("""We gave the value 0 through a data controller. The button
                  contains a trigger for a dataController that has a \"SET\" macro
                  that give \"36\" every time it is clicked""",
                  font_size='.9em', text_align='justify', colspan=2)
        fb.button('36',fire='^.my_button')
        fb.numberSpinner(lbl='number', value='^.number')
        
        fb.div("""This time the button contains directly the \"SET\" macro""",
                  font_size='.9em', text_align='justify', colspan=2)
        fb.button('36', action='SET .number2=36;')
        fb.numberSpinner(lbl='number 2', value='^.number2')