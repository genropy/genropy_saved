#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='hosting.client'
    py_requires="""public:Public,standard_tables:TableHandler,
                   gnrcomponents/selectionhandler,
                   hosted:HostedClient,hosted:HostedInstance"""

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Client'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'owner'
        
    def tableWriteTags(self):
        return 'owner'
        
    def tableDeleteTags(self):
        return 'owner'
        
    def barTitle(self):
        return '!!Client'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='10em')
        r.fieldcell('@user_id.username',name='User',width='10em')
        self.hosted_card_columns(r)

        return struct
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='code',op='contains', val='%')
    def orderBase(self):
        return 'code'

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        top = bc.borderContainer(region='top',height='120px')
        right = top.contentPane(region='right',width='350px')
        self.hosted_card_linker(right,disabled=disabled)
        center = top.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='3px',fld_width='100%',
                                width='350px',disabled=disabled)
        fb.field('code')
        fb.field('user_id')
              
        tc = bc.tabContainer(region='center')
        
        self.main_clienttab(tc.borderContainer(title='Info'),disabled)
        for pkgname,handler in [(c.split('_')[1],getattr(self,c)) for c in dir(self) if c.startswith('hostedclient_')]:
            handler(tc.contentPane(datapath='.hosted_data.%s' %pkgname,
                                title=self.db.packages[pkgname].name_long,
                                nodeId='hosted_client_data_%s' %pkgname,
                                sqlContextName='sql_record_hosted_client_%s' %pkgname,
                                sqlContextRoot='form.record.hosted_client_data'))
        
    
    def main_clienttab(self,bc,disabled):
        
        self.selectionHandler(bc.borderContainer(region='center'),label='!!Instances',
                                datapath="instances",nodeId='instances',table='hosting.instance',
                                struct=self.struct_instances,reloader='^form.record.id',
                                hiddencolumns='$site_path',
                                selectionPars=dict(where='$client_id=:c_id',c_id='=form.record.id',
                                                    applymethod='apply_instances_selection',order_by='$code'),
                                dialogPars=dict(height='400px',width='600px',formCb=self.instance_form,
                                                toolbarPars=dict(lock_action=True,add_action=True,del_action=True,save_action=True),
                                                default_client_id='=form.record.id',saveKwargs=dict(_lockScreen=True,saveAlways=True)))
                                                
    def instance_form(self,parentBC,disabled=None,table=None,**kwargs):
        tc = parentBC.tabContainer(**kwargs)
        self.main_instancetab(tc.contentPane(title='Info',_class='pbl_roundedGroup',margin='5px'),table=table,disabled=disabled)
        for pkgname,handler in [(c.split('_')[1],getattr(self,c)) for c in dir(self) if c.startswith('hostedinstance_')]:
            handler(tc.contentPane(datapath='.hosted_data.%s' %pkgname,title=self.db.packages[pkgname].name_long,
                                  nodeId='hosted_instance_data_%s' %pkgname,
                                sqlContextName='sql_record_hosted_instance_%s' %pkgname,
                                sqlContextRoot='instances.dlg.record.hosted_data.%s' %pkgname))
        
    def main_instancetab(self,parent,disabled=None,table=None):
        bc = parent.borderContainer()
        pane = bc.contentPane(region='top')
        pane.div('!!Manage instances', _class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, border_spacing='6px',dbtable=table,disabled=disabled)
        fb.field('code',width='15em',lbl='!!Instance Name')


        pane.dataRpc('.$creation_result', 'createInst', instance_code='=.code', instance_exists='=.$instance_exists', site_exists='=.$site_exists', 
                    _fired='^.$create',_onResult='FIRE .$created',_userChanges=True)
        pane.dataController("""
                if (site_path){
                SET .site_path=site_path;
                SET .$site_exists=true;
                }
                if (instance_path){
                SET .path=instance_path;
                SET .$instance_exists=true;
                }
                """,site_path='=.$creation_result.site_path',
                 instance_path='=.$creation_result.instance_path', 
                 _fired='^.$created',_userChanges=True)
        def struct(struct):
            r = struct.view().rows()
            r.cell('type', name='Slot type', width='15em')
            r.cell('qty', name='Q.ty', width='4em',dtype='I')
            return struct
        iv = self.includedViewBox(bc.borderContainer(region='center'),label='!!Slot configuration',
                         storepath='.slot_configuration', struct=struct,
                         datamode='bag',autoWidth=True,
                         add_action=True,del_action=True)
        gridEditor = iv.gridEditor()
        gridEditor.dbSelect(gridcell='type',dbtable='hosting.slot_type',
                         columns='$code,$description',rowcaption='$code',
                         exclude=True,hasDownArrow=True)
        gridEditor.numberTextBox(gridcell='qty')

    def onLoading_hosting_instance(self, record, newrecord, loadingParameters, recInfo):
        tblinstance = self.db.table('hosting.instance')           
        instance_exists = self.db.packages['hosting'].instance_exists(record['code'])
        site_exists = self.db.packages['hosting'].site_exists(record['code'])
        record.setItem('$instance_exists', instance_exists)
        record.setItem('$site_exists', site_exists)
    
    def rpc_apply_instances_selection(self,selection,**kwargs): 
        tblinstance = self.db.table('hosting.instance')       
        
        def apply_row(row):
            instance_exists = self.db.packages['hosting'].instance_exists(row['code'])
            site_exists = self.db.packages['hosting'].site_exists(row['code'])    
            if site_exists and instance_exists:
                return dict(create='<div class="greenLight"></div>')
            else:
                return dict(create='<div class="yellowLight"></div>')
        selection.apply(apply_row)
        
    def rpc_createInst(self,instance_code=None, instance_exists=None, site_exists=None):
        result = Bag()
        instancetbl=self.db.table('hosting.instance')
        if not instance_exists:
            result['instance_path']=instancetbl.create_instance(instance_code, self.site.instance_path, self.site.gnrapp.config)
        if not site_exists:
            result['site_path']=instancetbl.create_site(instance_code, self.site.site_path, self.site.config)
        return result
    
    def struct_instances(self,struct):
        r = struct.view().rows()
        r.fieldcell('code', width='10em')
        r.fieldcell('path', width='20em')
        r.cell('create',calculated=True,name='!!Status',width='10em')
        return struct

