# -*- coding: UTF-8 -*-


"""Buttons Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"    
    
    @example(code='1',height=150,description='xxxxxxx')
    def alert(self, pane):
        pane=pane.contentPane(background_color='pink')
        pane.button('Alert',action='alert("Alert")')
        
    def doc_alert(self):
        """
This is a button with an action parameter that has a js alert
blkzsd THIS COULD GO IN TAB 3 BUT WE HAVE IT ALSO IN THE CODE
dsfhdgf  h dfgh dfg df h dfgh d gh dfgh dfg hdgd
ghdfghdfghdfghdfghd
dfg
sdfg
sdf
gsdfgsdfgsdfgsfdfghdfgjfghjfghfghjfgh
            """
        
    @example(code='2',height=200,description='zzzz')
    def fooooooo(self, pane):
        """This is a button with an action parameter that has a js alert"""
        pane.button('Alert',action='alert("Alert")')
    
    @example(code='3',height=200,description='uuuuu')
    def baaaaar(self, pane):
        """This is a button with an action parameter that has a js alert"""
        pane.button('Alert',action='alert("Alert")')