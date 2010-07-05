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
    py_requires="""public:Public,standard_tables:TableHandler,sw_base_component:UtilitaAnagrafica,
                   gnrcomponents/selectionhandler,hosted:HostedClient,hosted:HostedInstance"""

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
        r.fieldcell('@anagrafica_id.ragione_sociale',name='!!Ragione sociale',width='15em')
        r.fieldcell('@user_id.username',name='User',width='10em')
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
        fb = right.formbuilder(cols=1,border_spacing='3px',disabled=disabled)
        self.anagrafica_linker(fb,field='anagrafica_id',width='20em',height='8ex',lbl='!!Anagrafica') 
        center = top.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='3px',fld_width='100%',
                                width='350px',disabled=disabled)
        fb.field('code')
        fb.field('user_id')
        #fb.field('anagrafica_id',colspan=2)
       
              
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
        
    def main_instancetab(self,pane,disabled=None,table=None):
        pane.div('!!Manage instances', _class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, border_spacing='6px',dbtable=table,disabled=disabled)
        fb.field('code',width='15em',lbl='!!Instance Name')
        fb.field('path',width='15em',lbl='!!Path')
        fb.field('site_path',width='15em',lbl='!!Site path')
        fb.button('Create', disabled='==_instance_exists&&_site_exists',
                    _instance_exists='=.$instance_exists',
                    _site_exists='^.$site_exists', action='FIRE .$create;')

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

