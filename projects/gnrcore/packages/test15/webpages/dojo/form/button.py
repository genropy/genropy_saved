# -*- coding: utf-8 -*-

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


    def test_5_shortcut(self, pane):
        """Shortcut f2"""
        tc = pane.tabContainer(height='300px',width='400px')
        p1 = tc.contentPane(title='Tab1')
        p2 = tc.contentPane(title='Tab2')
        p3 = tc.contentPane(title='Dialogs')
        p1.button('Quit', action='alert("Quit")',_shortcut='f2',nodeId='qtbtn')
        p1.button('Quot', action='alert("Quot")',_shortcut='f2',disabled='^.disabled_quot')
        p1.checkbox(value='^.disabled_quot',label='Disabled quot',default=True)
        box = p1.div(border='1px solid silver',margin='4px',padding='10px')
        p1.button('Create buttons',action="""
            var cb = function(){
                console.log(arguments);
            }
            box._('button',{action:cb,label:'Dynamic',_shortcut:'f2'});
            box._('button',{action:cb,label:'Dynamic 2',_shortcut:'f2',nodeId:'number2'});
            box._('button',{action:'genro.nodeById("number2")._destroy()',label:'kill 2'});
        """,box=box)
        p2.button('Marameo',action='alert("Marameo");',_shortcut='f2')
        
        dlg = p3.dialog(title='Hello',height='300px',width='400px',closable=True)
        p3.button('Open dialog', action='dlg.show()',dlg=dlg.js_widget)
        p3.button('Underdialog', action='alert("underdialog")',_shortcut='f2')
        dlg.button('Inside dialog', action='alert("Inside dialog")',_shortcut='f2')


    def test_6_ask(self, pane):
        """Ask button"""
        fb = pane.formbuilder(_anchor=True)
        fb.textbox(value='^.last_answer',lbl='Default answer')
        fb.button('Question', action='alert(answer);',
                    ask=dict(title='Do you want to rule?',
                            fields=[dict(name='answer',tag='filteringSelect',values='NO,YES',
                                        validate_onAccept="""SET #ANCHOR.last_answer=value"""),
                                        dict(name='serious', wdg='checkbox', label='Serious?')]),
                            answer='=.last_answer')
        