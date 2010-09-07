# -*- coding: UTF-8 -*-
# 
"""css3make tester"""

class GnrCustomWebPage(object):

    py_requires="gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme='claro'
    
  
    def test_1_rounded(self,pane):
        """rounded corners """
        css3make=self.utils.css3make
        pane.div(margin='5px',display='inline-block',border='1px solid gray',width='100px',height='80px',
            style=css3make(rounded='15'))
        pane.div(margin='5px',display='inline-block',border='1px solid gray',width='100px',height='80px',
            style=css3make(rounded='all:12,tl:0,br:0'))
        pane.div(margin='5px',display='inline-block',border='1px solid gray',width='100px',height='80px',
            style=css3make(rounded='top:4,bottom:14'))
        pane.div(margin='5px',display='inline-block',border='1px solid gray',width='100px',height='80px',
            style=css3make(rounded='left:2,right:14'))
       