# -*- coding: UTF-8 -*-


"""Buttons Examples Advanced"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"
    
    @example(code='1',height='200',description='Icon Button setting a spinner widget value using the SET macro')
    def iconbutton(self, pane):
        fb = pane.formbuilder(cols=2, margin='5px')
        fb.button('Show screen resolution', showLabel=False,
                   action="SET .res = screen.width+' x '+screen.height;",
                   iconClass='iconbox spanner')
        fb.textbox(lbl='Screen Res:',value='^.res', width='7em')
        
    def doc_iconbutton(self):
        """This example shows how to create an icon button.  The 1st parameter becomes the tooltip parameter. 
showlabel='False' removes the button label.
The action parameter uses the SET macro. is sets a value of a path in the datastore.  In this case it is using the js functions screen width
and screen height in a text snippet.  This text snippet is set to '.res path in the datastore.

The iconClass refers to the css class containing the iconbox and spanner.
Notice in this example that we have used a formbuilder widget to contan both the button and the field widget.
"""

    @example(code='2',height='280',description='Button with action showing the use of macro FIRE')
    def button_fire(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.dataController('''alert(msg);''', msg='^.msg')
        fb.button('Button 1',action="FIRE .msg='Click';")
        fb.div(""" "action="FIRE msg='Click';" [shows an alert message reporting "Click"] """,
                                                                            font_size='.9em')
        fb.button('Button 2',fire_Click = '.msg')
        fb.div(""" "fire_Click = 'msg'" [same result of the previous one]""",font_size='.9em')
        fb.button('Button 3',fire='.msg')
        fb.div(""" "fire='msg'" [shows an alert message reporting "true"] """,font_size='.9em')

    def doc_button_fire(self):
        """This example shows the use of the FIRE macro.  To recap the macros SET, FIRE, GET and PUT are js methods providing shortcut to execute them.
We start with a controller called a dataController. 1st parameter is the js to execute, 
and the subsequent parameters sets the js variables from the datastore. Remember the ^ is an observer so that as soon as the
datastore value at that path changes, then it fires the dataController.

There are three variations of FIRE.  The 1st variation sets the value 'Click' at path '.msg'
(note is it s relative path so do not forget the period).
The 2nd variation has the same result but with a different syntax, meaning that you can set the value by the suffix after 'fire_'.
We will see advantage to this way later.
The 3rd variation sets the path '.msg' with the value true.


"""

