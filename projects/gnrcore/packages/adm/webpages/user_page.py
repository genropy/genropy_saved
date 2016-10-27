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
        self.loginData(bc.roundedGroup(title='Login',region='top',datapath='.record',height='200px'))
        center = bc.tabContainer(region='center',margin='2px')

        self.userAuth(center.contentPane(title='Auth'))
        self.qtreeConf(center.contentPane(title='Quick tree conf'))

    
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
                            pbl_classes=True,margin='2px',addrow=False,picker='tag_id',
                            picker_condition='$child_count=0',
                            picker_viewResource=True)


    def qtreeConf(self,pane):
        pane.inlineTableHandler(relation='@custom_info',viewResource='QTreeViewFromUser',
                            pbl_classes=True,margin='2px',condition='$info_type=:it',condition_it='QTREE')
 

    def qtreeConf_zz(self,sc):
        th_all = sc.contentPane(title='View').inlineTableHandler(table='adm.user_tblinfo',
                            viewResource='QTreeViewFromUserRO',
                            nodeId='QTREEEDit',
                            margin='2px',
                            condition="""($user_group IS NULL OR $user_group=:gc) AND 
                                        ($user_id IS NULL OR $user_id=:uid)""",
                            condition_gc='^#FORM.record.group_code',
                            condition_uid='^#FORM.record.id',condition_if='uid')
        th_all.view.top.bar.replaceSlots('vtitle','parentStackButtons')
        th_edit = sc.contentPane(title='Edit').inlineTableHandler(relation='@custom_info',viewResource='QTreeViewFromUser',
                            nodeId='QTREEView',datapath='#FORM.qtreeedit',
                            margin='2px')
        th_edit.view.top.bar.replaceSlots('vtitle','parentStackButtons')


    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        if recordCluster['md5pwd']:
            recordCluster.setItem('md5pwd', hashlib.md5(recordCluster.pop('md5pwd')).hexdigest())
