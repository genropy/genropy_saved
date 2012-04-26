#!/usr/bin/env python
# encoding: utf-8
"""button.py"""
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import inspect


class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer(region='center',datapath='main')
        self.top(bc.contentPane(region='top',height='100px',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        bottom=bc.borderContainer(region='center')
        left = bottom.borderContainer(region='left',width='50%')
        right = bottom.borderContainer(region='center',width='50%')
        
        self.example1(left.borderContainer(region='top',height='33%',margin='5px'))
        self.example3(left.contentPane(region='center',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        self.example5(left.contentPane(region='bottom',height='33%',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        
        self.example2(right.contentPane(region='top',height='33%',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        self.example4(right.contentPane(region='center',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        self.example6(right.contentPane(region='bottom',height='33%',_class='pbl_roundedGroup',margin='5px',background_color='white'))

    def top(self,pane):
        pane.div('Buttons and Button Actions, Graphical options, macros FIRE and SET',_class='pbl_roundedGroupLabel')
        desc = """The 'button' widget can be called from another widget such as a pane or formbuilder. The 1st parameter is the button label.
                  Then keyword parameters can be used to specify tooltip, width, font, font_size, height, etc, may be included.
                  The 'action' parameter is the javascript to be called when the button is clicked.  This page shows the FIRE and SET macros
                  which are js short cuts.</BR>
                  'FIRE' can be used in 3 ways.  'FIRE' will set data (by default True) to a datastore path, and then return to False or None</BR>
                  'SET' will set data to a datastore path
                  """
        pane.div(desc, margin='5px')

    def example1(self,bc,**kwargs):
        bc.data('^.example1.selectePage','demo')
        mydiv = bc.div('Simple Alert',_class='pbl_roundedGroupLabel', color='white')
        mydiv.button('Display source', position='relative',left='40px',bottom='4px',action="SET .example1.selectePage='doc'")
        mydiv.button('Display Example', position='relative',left='40px',bottom='4px',action="SET .example1.selectePage='demo'")
        sc = bc.stackContainer(region='center',selectedPage='^.example1.selectePage',nodeid='example1')
        self.example1_demo(sc.contentPane(region='center',margin='5px,5px 5px 5px',background_color='white',pageName='demo',_class='pbl_roundedGroup'))
        self.example1_doc(sc.contentPane(region='center',margin='5px,5px 5px 5px',background_color='white',pageName='doc',_class='pbl_roundedGroup'))

    def example1_demo(self,pane,**kwargs):
        pane.button('Alert', action="alert('Hello!')",margin='1em')

    def example1_doc(self,pane,**kwargs):
        desc = highlight(inspect.getsource(self.example1_demo), PythonLexer(), HtmlFormatter())
        pane.div(desc, margin='1em')




    def example2(self,pane):
        pane.div('Alert with supporting parameters',_class='pbl_roundedGroupLabel', color='white')
        desc = """fb.data('.icon','icnBaseOk')</BR>
        fb.button('alert', action="alert('Hello!')",</BR>
        &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        tooltip='click me!', width='30px', height='30px',</BR>
        &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        font_size='22px', font_family='Courier',</BR>
        &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        rounded=5, border='2px solid gray',</BR>
        &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        iconClass='^.icon')
        """
        pane.div(desc, margin='1em',font_family='Courier')
        fb = pane.formbuilder(cols=1)
        fb.data('.icon','icnBaseOk')
        fb.button('Alert', action="alert('Hello!')", tooltip='Please click me!', width='7.5em',
                          height='30px', font_size='22px', font_family='Courier',
                          rounded=5, border='2px solid gray',
                          iconClass='^.icon')


    def example3(self,pane):
        pane.div('Simple Confirm',_class='pbl_roundedGroupLabel', color='white')
        desc = """fb.button('Confirm', action="var r=confirm("Are you sure?");</BR>
        &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        if (r==true) { alert("You pressed OK!");} </BR>
        &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
        else {alert("You pressed Cancel!");}")"""
        pane.div(desc,margin='1em',font_family='Courier')
        fb = pane.formbuilder(cols=1)
        fb.button('Confirm', action="""var r=confirm("Are you sure?");
                                             if (r==true) { alert("You pressed OK!");}
                                             else {alert("You pressed Cancel!");}""")

    def example4(self,pane):
        pane.div('Evaluate your screen resolution',_class='pbl_roundedGroupLabel', color='white')
        desc = """
               fb.button('Show screen resolution', showLabel=False,</BR>
               &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
               action="SET .res = screen.width+' x '+screen.height;",</BR>
               &#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;
               iconClass='iconbox spanner')</BR>
               fb.textbox(lbl='Screen Res:',value='^.res', width='7em')
               """
        pane.div(desc,margin='1em',font_family='Courier')
        fb = pane.formbuilder(cols=2)
        fb.button('Show screen resolution', showLabel=False,
                   action="SET .res = screen.width+' x '+screen.height;",
                   iconClass='iconbox spanner')
        fb.textbox(lbl='Screen Res:',value='^.res', width='7em')

    def example5(self,pane):
        pane.div('Using the macro FIRE (3 different ways)',_class='pbl_roundedGroupLabel', color='white')
        desc = """
               fb = pane.formbuilder(cols=2)</BR>
               fb.button('Button 1',action="FIRE .msg='Click';")</BR>
               fb.button('Button 2',fire_Click = '.msg')</BR>
               fb.dataController('''alert(msg);''', msg='^.msg')</BR>
               fb.button('Button 3',fire='.msg')
               """
        pane.div(desc,margin='1em',font_family='Courier')
        fb = pane.formbuilder(cols=2)
        fb.dataController('''alert(msg);''', msg='^.msg')
        fb.button('Button 1',action="FIRE .msg='Click';")
        fb.div(""" "action="FIRE msg='Click';" [shows an alert message reporting "Click"] """,font_size='.9em')
        fb.button('Button 2',fire_Click = '.msg')
        fb.div(""" "fire_Click = 'msg'" [same result of the previous one]""",font_size='.9em')
        fb.button('Button 3',fire='.msg')
        fb.div(""" "fire='msg'" [shows an alert message reporting "true"] """,font_size='.9em')

    def example6(self,pane):
        pane.div('Using the macro SET',_class='pbl_roundedGroupLabel', color='white')
        desc = """
               fb.data('.number',0) <I># sets the initial value for path '.number'</I> </BR> 
               fb.button('36', action='SET .number=36;')</BR>
               fb.numberSpinner(lbl='number', value='^.number')
               """
        pane.div(desc,margin='1em',font_family='Courier')
        fb = pane.formbuilder(cols=2)
        fb.data('.number',0) # sets the initial value for path '.number'
        fb.button('Set 36 to spinner', action='SET .number=36;')
        fb.numberSpinner(lbl='number', value='^.number')

