# -*- coding: UTF-8 -*-


"""Buttons Examples"""

from gnr.core.gnrdecorator import example
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/examplehandler:ExampleHandlerFull"    
    
    @example(code='1',height=150,description='xxxxxxx',background_color='red')
    def alert(self, pane):
        """This is a button with an action parameter that has a js alert"""
        pane.button('Alert',action='alert("Alert")')
        
    @example(code='2',height=200,description='zzzz',background_color='red')
    def fooooooo(self, pane):
        """This is a button with an action parameter that has a js alert"""
        pane.button('Alert',action='alert("Alert")')
    
    @example(code='3',height=200,description='uuuuu')
    def baaaaar(self, pane):
        """This is a button with an action parameter that has a js alert"""
        pane.button('Alert',action='alert("Alert")')