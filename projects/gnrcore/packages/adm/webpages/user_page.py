# -*- coding: UTF-8 -*-

# user_page.py
# Created by Francesco Porcari on 2011-04-08.
# Copyright (c) 2011 softwell All rights reserved.
import hashlib

class GnrCustomWebPage(object):
    py_requires = """public:TableHandlerMain,
                   foundation/macrowidgets:RichTextEditor,
                    gnrcomponents/htablehandler:HTableHandlerBase"""
    maintable = 'adm.user'

    def windowTitle(self):
        return '!!User'

    def barTitle(self):
        return '!!Users'
    
    def th_form(self,form,**kwargs):
        bc = form.center.borderContainer()
        if 'th_linker' in self._call_kwargs:
            self.loginData(bc.borderContainer(region='top',datapath='.record',margin='2px',height='180px',_class='pbl_roundedGroup'))
            self.userAuth(bc.contentPane(region='center'))
        
        else:
            top = bc.borderContainer(region='top',height='30%')
            self.loginData(top.contentPane(region='left',width='40%',datapath='.record',margin='2px',_class='pbl_roundedGroup'))
            self.userAuth(top.contentPane(region='center',margin='2px'))
            tc = bc.tabContainer(region='center')
            tc.contentPane(title='Test')
        
    
    def loginData(self,pane):
        pane.div('!!Login Data', _class='pbl_roundedGroupLabel')
        fb = pane.div(margin='5px').formbuilder(cols=2, border_spacing='6px',width='100%',fld_width='100%')
        fb.field('firstname',lbl='!!Firstname')
        fb.field('username',lbl='!!Username',validate_nodup=True,validate_notnull_error='!!Exists')
        fb.field('lastname',lbl='!!Lastname')
        fb.textBox(value='^.md5pwd', lbl='Password', type='password',validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('status', tag='filteringSelect', # values='!!conf:Confirmed,wait:Waiting', 
                 validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('avatar_rootpage',lbl='!!Startpage',tip='!!User start page',colspan=2)
        fb.field('email', lbl='!!Email',colspan=2)
        fb.field('sms_login', html_label=True,colspan=2)
        fb.field('sms_number',row_hidden='^.sms_login?=!#v',colspan=2)
        fb.field('locale', lbl='!!Locale')

    def userAuth(self,pane):
        pane.inlineTableHandler(relation='@tags',viewResource=':ViewFromUser',autoSave=False,semaphore=False,pbl_classes=True,margin='2px')

        

    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        if recordCluster['md5pwd']:
            recordCluster.setItem('md5pwd', hashlib.md5(recordCluster.pop('md5pwd')).hexdigest())
