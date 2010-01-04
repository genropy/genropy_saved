#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='base.staff'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'
    js_requires='common'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Staff'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Staff'
        
    def columnsBase(self,):
        return """@user_id.username,@user_id.auth_tags,roles"""
            
    def orderBase(self):
        return '@user_id.username'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='@user_id.username',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        bc.dataController("""var tag_list = tags.split(',');
                             var cb = function(node,kw,idx){
                                var attr = node.attr;
                                attr['checked'] = dojo.indexOf(tag_list,attr['tagname'])>-1?true:false;
                             }
                             tag_sel.walk(cb);
                                """,
                            tag_sel="=.tag_selection",tags='=.@user_id.auth_tags',
                            _fired='^.id',_if='tags')
        bc.dataController("""var roles = roles.split(',');
                             var cb = function(node,kw,idx){
                                var attr = node.attr;
                                attr['checked'] = dojo.indexOf(roles,attr['description'])>-1?true:false;
                             }
                             role_sel.walk(cb);
                                """,
                            role_sel="=.role_selection",roles='=.roles',
                            _fired='^.id',_if='roles')
        self.staffForm(bc.contentPane(region='top',_class='pbl_roundedGroup',height='40%',margin='5px'),disabled=disabled)
        self.tagsAndRoles(bc.borderContainer(region='center'),disabled=disabled)
        
    def staffForm(self,pane,disabled=None):
        pane.div('!!Base Info',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1,border_spacing='4px',dbtable='adm.user',
                              datapath='.@user_id',disabled=disabled)
        fb.field('username',width='15em',lbl='!!Username')
        fb.field('firstname',width='15em',lbl='!!Firstname')
        fb.field('lastname',width='15em',lbl='!!Lastname')
        fb.textBox(value='^.md5pwd',lbl='Password', type='password')
        fb.field('status',tag='filteringSelect',values='!!conf:Confirmed,wait:Waiting',width='15em',
                validate_notnull=True,validate_notnull_error='!!Required')
                
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr):
        userRecord = recordCluster['@user_id']
        if userRecord['md5pwd']:
            tblobj = self.db.table('adm.user')
            userid =tblobj.newPkeyValue()
            userRecord['id'] = userid
            userRecord.setItem('md5pwd',self.application.changePassword(False,False,userRecord.pop('md5pwd'),userid))
                
    def tagsAndRoles(self,bc,disabled=False):
        self.includedViewBox(bc.borderContainer(region='left',margin='5px',width='50%',margin_top=0),
                              label='!!Tags',storepath='.tag_selection',
                              nodeId='tagView',table='adm.tag',autoWidth=True,
                              struct=self.tags_struct)
                              
        self.includedViewBox(bc.borderContainer(region='center',margin='5px',
                                                margin_left=0,margin_top=0),
                              label='!!Roles',storepath='.role_selection',
                              nodeId='roleView',table='base.role',autoWidth=True,
                              struct=self.roles_struct)
                              
    def tags_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tagname',name='Tag',width='5em')
        r.fieldcell('description',name='Tag',width='25em')
        r.cell('checked',name=' ',width='2em',
                format_trueclass='checkboxOn',
                    styles='background:none!important;border:0;',
                    format_falseclass='checkboxOff',
                     format_onclick='staff.check_row(kw.rowIndex, e, this,"tags");',
                    dtype='B',calculated=True)
        return struct
        
    def rpc_tagchecker(self,selection):
        pass
        
    def roles_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description',name='Tag',width='30em')
        r.cell('checked',name=' ',width='2em',
                format_trueclass='checkboxOn',
                    styles='background:none!important;border:0;',
                    format_falseclass='checkboxOff',
                     format_onclick='staff.check_row(kw.rowIndex, e, this,"roles");',
                    dtype='B',calculated=True)
        return struct
        
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr):
        #devo capire meglio come funzionano i changes
        #forse non vengono prese come changes in quanto non tocco i valori
        pass
        
    def onLoading(self,record,newrecord,loadingParameters,recInfo):
        tag_selection = self.db.table('adm.tag').query(order_by='tagname').selection()
        role_selection = self.db.table('base.role').query(order_by='description').selection()
        record['tag_selection'] = tag_selection.output('grid')
        record['role_selection'] = role_selection.output('grid')
        #manca un out_ nel sqldata che simuli effettivamente quello che abbiamo con un dataselection
        #in quanto la app getSelection effettua delle modifiche su la selezione. io porterei lo stesso
        #meccanismo a livello di sqldata
        
        
        
        