# -*- coding: UTF-8 -*-

"""Buttons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic button"""
        pane.button('i am a button', action='console.log("you clicked me ",event,_counter)',_delay=50)
        
    def test_2_styled(self, pane):
        """Styled button"""
        pane.button('i am a button',
                     action="""var pippo = confirm("Format your PC/Mac?");
                               if (pippo == true){alert("formatted!")};""",
                     style='color:red;font-size:44px;')
                    
    def test_3_params(self, pane):
        """Button with action and action parameters"""
        pane.textbox(value='^msg')
        pane.button('i am a button', action='alert(msg)', msg='=msg',ask=dict(title='TEst',fields=[dict(name='msg',lbl='Message')]))

    def test_4_divbutton(self, pane):
        pane.lightbutton('i am a button', action='alert(msg)', msg='=msg',
                        ask=dict(title='Test',fields=[dict(name='msg',lbl='Message')]))

