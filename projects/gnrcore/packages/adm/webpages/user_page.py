# -*- coding: utf-8 -*-

# user_page.py
# Created by Francesco Porcari on 2011-04-08.
# Copyright (c) 2011 softwell All rights reserved.
from builtins import object
import hashlib

class GnrCustomWebPage(object):
    py_requires = """public:TableHandlerMain"""
    maintable = 'adm.user'

    def windowTitle(self):
        return '!!User'

    def barTitle(self):
        return '!!Users'
    
    def th_form(self,form,**kwargs):
        bc = form.center.borderContainer()
        self.loginData(bc.roundedGroup(title='Login',region='top',datapath='.record',height='200px'))
        center = bc.tabContainer(region='center',margin='2px')

        self.userAuth(center.contentPane(title='Auth'))
        self.userConfigView(center.contentPane(title='Config'))
    
    def loginData(self,pane):
        fb = pane.div(margin_right='10px').formbuilder(cols=2, border_spacing='4px',colswidth='12em')
        fb.field('firstname',lbl='!!Firstname')
        fb.field('lastname',lbl='!!Lastname')

        fb.field('username',lbl='!!Username',validate_nodup=True,validate_notnull_error='!!Exists')
        fb.textBox(value='^.md5pwd', lbl='Password', type='password',validate_notnull=True, validate_notnull_error='!!Required')
        
        fb.field('status', tag='filteringSelect', # values='!!conf:Confirmed,wait:Waiting', 
                 validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('group_code')
        fb.field('locale', lbl='!!Locale')
        fb.field('avatar_rootpage',lbl='!!Startpage',tip='!!User start page')
        fb.field('email', lbl='!!Email',colspan=2,width='100%')
        fb.field('sms_login', html_label=True)
        fb.field('sms_number',hidden='^.sms_login?=!#v',colspan=2,width='100%')

    def userAuth(self,pane):
        pane.inlineTableHandler(relation='@tags',viewResource='ViewFromUser',
                            pbl_classes=True,margin='2px',addrow=True,picker='tag_id',
                            picker_condition='$child_count=0',
                            picker_viewResource=True)

    def userConfigView(self,pane):
        pane.dialogTableHandler(table='adm.user_config',margin='2px',
                                viewResource='ViewFromUser',
                                formResource='FormFromUser')

    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        if recordCluster['md5pwd']:
            recordCluster.setItem('md5pwd', hashlib.md5(recordCluster.pop('md5pwd').encode()).hexdigest())
