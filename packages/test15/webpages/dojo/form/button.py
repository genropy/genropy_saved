# -*- coding: UTF-8 -*-
# 
"""Buttons"""

class GnrCustomWebPage(object):

    py_requires="gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme='claro'
    
    def test_1_basic(self,pane):
        """Basic button"""
        pane.button('i am a button',action='alert("you clicked me")')
        
    def test_2_styled(self,pane):
        """Styled button"""
        pane.button('i am a button',action='alert("you clicked me")',
                        style='color:red;font-size:44px;')
                        
    def test_3_types(self,pane):
        """Different button types"""
        pane.data('icon','icnBaseOk')
        pane.data('fontType','Courier')
        pane.dataController("""alert(msg);""",msg='^msg')
        bc = pane.borderContainer()
        fb = bc.formbuilder(cols=2)
        fb.div('button type')
        fb.button(action="FIRE msg='Saving!';",iconClass='^icon',
                   tooltip='click me!',font_family='^fontType',label='Save it')
        fb.div('checkbox type')
        self.checkBoxGroup(fb,'First,Second,Third')
        self.makeDropDown(fb,'Menù')
        
    def makeDropDown(self,pane,label):
        pane.div('dropdownbutton type')
        ddb=pane.dropdownbutton(label)
        dmenu=ddb.menu()
        dmenu.menuline('Open...', action="FIRE msg='Opening!';")
        dmenu.menuline('Close', action="FIRE msg='Closing!';")
        dmenu.menuline('-')
        submenu=dmenu.menuline('I have submenues').menu()
        submenu.menuline('To do this', action="alert('Doing this...')")
        submenu.menuline('Or to do that', action="alert('Doing that...')")       
        dmenu.menuline('-')
        dmenu.menuline('Quit',action="alert('Quitting...')")
        
    def checkBoxGroup(self,pane,labels,columns=1):
        labels=labels.split(',')
        pane=pane.formbuilder(cols=columns)
        for label in labels:
            pane.checkbox(value='^cb_%s' %label,label=label)