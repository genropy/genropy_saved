# -*- coding: UTF-8 -*-
# 
"""Buttons"""

class GnrCustomWebPage(object):

    py_requires="testhandler:TestHandlerBase"
    dojo_theme='claro'
    
    def test_1_basic(self,pane):
        """Basic button"""
        pane.button('i am a button',action='alert("you clicked me")')
        
    def test_2_styled(self,pane):
        """Styled button"""
        pane.button('i am a button',action='alert("you clicked me")',
                        style='color:red;font-size:44px;')
  
