# -*- coding: UTF-8 -*-
"""contentPane"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic contentPane"""
        bc = pane.borderContainer(margin='3px', height='600px')
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='1px',height='40%')
        top.div('!!Registry records',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(margin_left='10px',margin_top='1em',width='370px',cols=2)
        fb.textbox(lbl='Name')
        fb.textbox(lbl='Surname')
        fb.textbox(lbl='Email')
        fb.textbox(lbl='Telephone')
        fb.textbox(lbl='Tax code')
        fb.textbox(lbl='VAT')
        fb.textbox(lbl='Fax',colspan=2,width='100%')
        fb.textArea(lbl='Notes',colspan=2,width='100%')
        fb.filteringSelect(lbl='Company role', values='E:emplyee, F:freelance, M:manager, O:owner')
        
        left = bc.contentPane(region='left',_class='pbl_roundedGroup',margin='1px',width='50%')
        left.div('!!Staff records',_class='pbl_roundedGroupLabel')
        fb = left.formbuilder(margin_left='10px',margin_top='1em',width='370px')
        fb.textbox(lbl='Internal number',placeholder='example: 202')
        fb.textbox(lbl='Notes',placeholder='Write your notes here')
        
        right = bc.contentPane(region='center',_class='pbl_roundedGroup',margin='1px',width='50%')
        right.div('!User records',_class='pbl_roundedGroupLabel')
        fb = right.formbuilder(margin_left='10px',margin_top='1em',width='370px')
        fb.textbox(lbl='Username')
        fb.textbox(lbl='md5pwd')
        fb.textbox(lbl='Auth tags')
        fb.textbox(lbl='Avatar rootpage')