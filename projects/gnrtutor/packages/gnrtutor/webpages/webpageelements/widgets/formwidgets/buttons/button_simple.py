# -*- coding: UTF-8 -*-


"""Standard Buttons Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"    
    
    @example(code='1',height=120,description='This is a button with an action parameter that has a js alert')
    def alert(self, pane):
        pane.button('Alert',action='alert("Alert")', margin='5px')
        
    def doc_alert(self):
        """This example shows how to create a button.  Yes it is that simple!  The interface objects pane, div, formbuilder, etc all have the attribute 'button'
so you just call it and pass a few parameter.  The first parameter is the button label. 
The next important named parameter 'action='my_javasscript', is where you pass some javascript to it.  
The 'button' widget can be called from another widget such as a pane or formbuilder (discussed elsewhere).
"""

    @example(code='2',height=200,description='Button Alert with graphical parameters')
    def alert2(self, pane):
        pane.data('.icon','icnBaseOk')
        pane.button('alert', action="alert('Hello!')",
                   tooltip='click me!', width='10em', height='30px',
                   font_size='22px', font_family='Courier',
                   rounded=5, border='2px solid gray',
                   iconClass='^.icon')
    def doc_alert2(self):
        """This example shows how to create a button that has further graphical elements.
We have passed tooltip parameter to display some mouseover helpl; a font_family, and a rounding for the button edges; and a border.

A button can include an icon. In a css file we can specify the class which specifies the icon path and other related parameters.
This example demonstrates the use of a controller named 'data'.  It is an attribute of the pane.
Its use is to SET an initial value into a path in the datastore. In this case it is setting the css class.
"""
    
    @example(code='3',height=150,description='Button with confirm js example')
    def confirm(self, pane):
        pane.button('Confirm', action="""var r=confirm("Are you sure?");
                                             if (r==true) { alert("You pressed OK!");}
                                             else {alert("You pressed Cancel!");}""")
    def doc_confirm(self):
        """This example is showing some more complex js"""


    @example(code=4,height='200',description='Icon Button setting a spinner widget value using the SET macro')
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

    @example(code=5,height='280',description='Button with action showing the use of macro FIRE')
    def button_fire(self, pane):
        fb = pane.formbuilder(cols=2, margin='5px')
        fb.dataController('''alert(msg);''', msg='^.msg')
        fb.button('Button 1',action="FIRE .msg='Click';")
        fb.div(""" "action="FIRE msg='Click';" [shows an alert message reporting "Click"] """,
                                                                            font_size='1em')
        fb.button('Button 2',fire_Click = '.msg')
        fb.div(""" "fire_Click = 'msg'" [same result of the previous one]""",font_size='1em')
        fb.button('Button 3',fire='.msg')
        fb.div(""" "fire='msg'" [shows an alert message reporting "true"] """,font_size='1em')

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


    @example(code=6,height='200',description='Button with action showing the use of macro SET with data controller')
    def button_set(self, pane):
        fb = pane.formbuilder(cols=2, margin='5px')
        fb.data('.number',1) # sets the initial value for path '.number'
        fb.button('Set 36 to spinner', action='SET .number=36;')
        fb.numberSpinner(lbl='number', value='^.number',bazinga=True)

    def doc_button_set(self):
        """This example shows the use of the SET macro.  We are using a formbuilder again which is a genro tool to create an html table.
Each column of the formbuilder is equivilent to 2 columns of a table, the first being the column for the label and the second the column
for the widget (usually a field widget).

We then use the controller 'data' to set the initial value of the bag at the path '.number' to zero.
The button has the action SET which sets the value 36 to the bag at path '.number' to 36.

The numberSpinner widget is fired to change its value because of the observer ^ on path '.number'
"""
        