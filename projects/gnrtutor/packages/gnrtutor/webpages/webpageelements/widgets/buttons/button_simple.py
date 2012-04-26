# -*- coding: UTF-8 -*-


"""Buttons Examples Simple"""

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
        