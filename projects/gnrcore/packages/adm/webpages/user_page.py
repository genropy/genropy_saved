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
            self.loginData(bc.borderContainer(region='top',datapath='.record',margin='2px'))
            self.userAuth(bc.contentPane(region='center',margin='2px'))
        
        else:
            top = bc.borderContainer(region='top',height='30%')
            self.loginData(top.contentPane(region='left',width='40%',datapath='.record',margin='2px',_class='pbl_roundedGroup'))
            self.userAuth(top.contentPane(region='center',margin='2px'))
            tc = bc.tabContainer(region='center')
            tc.contentPane(title='Test')
        
    
    def loginData(self,pane):
        pane.div('!!Login Data', _class='pbl_roundedGroupLabel')
        fb = pane.div(margin='5px').formbuilder(cols=2, border_spacing='6px',width='100%',fld_width='100%')
        fb.field('username',lbl='!!Username',validate_nodup=True,validate_notnull_error='!!Exists')
        fb.field('firstname',lbl='!!Firstname')
        fb.field('lastname',lbl='!!Lastname')
        fb.textBox(value='^.md5pwd', lbl='Password', type='password',validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('status', tag='filteringSelect', values='!!conf:Confirmed,wait:Waiting', 
                 validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('avatar_rootpage',lbl='!!Startpage',tip='!!User start page',colspan=2)
        fb.field('adm.user.email', lbl='!!Email')

    
    def userAuth(self,pane):
        th = pane.plainTableHandler(relation='@tags',viewResource=':ViewFromUser')
        bar = th.view.top.bar        
        bar.replaceSlots('#','#,delrow,addtags')
        bar.addtags.paletteTree('htags', title='Tags',tree_persist=True,
                                dockButton_iconClass='icnOpenPalette',height='250px',width='180px'
                                ).htableStore('adm.htag')
        grid = th.view.grid
        grid.dragAndDrop(dropCodes='htags')
        grid.dataRpc('dummy','addTags',data='^.dropped_htags',user_id='=#FORM.pkey')
    
    def rpc_addTags(self,data=None,user_id=None,**kwargs):
        usertagtbl = self.db.table('adm.user_tag')
        tag_id = data['pkey']
        if usertagtbl.query(where='$user_id=:user_id AND $tag_id=:tag_id',tag_id=tag_id,user_id=user_id).count()==0:
            usertagtbl.insert(dict(user_id=user_id,tag_id=tag_id))
            self.db.commit()
        

    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        if recordCluster['md5pwd']:
            recordCluster.setItem('md5pwd', hashlib.md5(recordCluster.pop('md5pwd')).hexdigest())
