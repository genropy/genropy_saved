# -*- coding: UTF-8 -*-

# contentpane.py
# Created by Filippo Astolfi on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        bc = root.borderContainer(margin='3px')
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
        fb.combobox(lbl='Company role',values='emplyee, freelance, manager, owner')
        
        left = bc.contentPane(region='left',_class='pbl_roundedGroup',margin='1px',width='50%')
        left.div('!!Staff records',_class='pbl_roundedGroupLabel')
        fb = left.formbuilder(margin_left='10px',margin_top='1em',width='370px')
        fb.textbox(lbl='Internal number',ghost='example: 202')
        fb.textbox(lbl='Notes',ghost='example: 202')
        
        right = bc.contentPane(region='center',_class='pbl_roundedGroup',margin='1px',width='50%')
        right.div('!User records',_class='pbl_roundedGroupLabel')
        fb = right.formbuilder(margin_left='10px',margin_top='1em',width='370px')
        fb.textbox(lbl='Username')
        fb.textbox(lbl='md5pwd')
        fb.textbox(lbl='Auth tags')
        fb.textbox(lbl='Avatar rootpage')
    