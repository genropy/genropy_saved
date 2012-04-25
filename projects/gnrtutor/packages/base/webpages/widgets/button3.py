# -*- coding: UTF-8 -*-


"""Buttons Examples : why not this docline ???"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/examplehandler:ExampleHandlerFull"    

    def example_1_alert(self, pane):
        """This is a button with an action parameter that has a js alert"""
        box_height=300
        pane.button('Alert',action='alert("Alert")')

    def example_2_fooooooo(self, pane):
        """This is a button with an action parameter that has a js alert"""
        box_height=200
        pane.button('Alert',action='alert("Alert")')
    

    def example_3_baaaaar(self, pane):
        """This is a button with an action parameter that has a js alert"""
        box_height=400
        pane.button('Alert',action='alert("Alert")')