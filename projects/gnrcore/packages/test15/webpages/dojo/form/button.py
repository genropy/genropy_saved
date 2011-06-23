# -*- coding: UTF-8 -*-

"""Buttons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'
    dojo_version='16'
    
    def test_1_basic(self, pane):
        """Basic button"""
        pane.button('i am a button', action='alert("you clicked me")')
        
    def test_2_styled(self, pane):
        """Styled button"""
        pane.button('i am a button',
                     action="""var pippo = confirm("Format your PC/Mac?");
                               if (pippo == true){alert("formatted!")};""",
                     style='color:red;font-size:44px;')
                    
    def test_3_params(self, pane):
        """Button with action and action parameters"""
        pane.textbox(value='^msg')
        pane.button('i am a button', action='alert(msg)', msg='=msg')