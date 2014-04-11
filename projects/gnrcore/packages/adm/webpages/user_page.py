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
        self.loginData(bc.roundedGroup(title='Login',region='top',datapath='.record',height='180px'))
        self.userAuth(bc.contentPane(region='center'))
    
    
    def loginData(self,pane):
        fb = pane.div(margin_right='10px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='100%',colswidth='auto')
        fb.field('firstname',lbl='!!Firstname')
        fb.field('lastname',lbl='!!Lastname')
        fb.field('username',lbl='!!Username',validate_nodup=True,validate_notnull_error='!!Exists')
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
