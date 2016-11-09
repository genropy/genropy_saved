#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group',hidden='^#mainpars.user_group',width='6em')
        r.fieldcell('username',hidden='^#mainpars.username',width='7em')
        r.fieldcell('pkgid',hidden='^#mainpars.pkgid',width='4em')
        r.fieldcell('tblid',hidden='^#mainpars.tblid',width='8em')
        r.fieldcell('data')

    def th_hiddencolumns(self):
        return '$rank'

    def th_order(self):
        return 'rank:a'

    def th_condition(self):
        return dict(condition="""(:ugroup IS NULL OR $user_group=:ugroup) AND
                                (:uid IS NULL OR $username=:uid) AND
                                (:pkginfo IS NULL OR $pkgid=:pkginfo) AND
                                (:tblinfo IS NULL OR $tblid=:tblinfo)
                            """,condition_ugroup='^#mainpars.user_group',
                                 condition_uid='^#mainpars.username',
                                 condition_tblinfo='^#mainpars.tblid',
                                 condition_pkginfo='^#mainpars.pkgid'
                                 )

class Form(BaseComponent):
    js_requires = 'adm_configurator'
    def th_form(self,form):
        form.store.handler('save',onSaving="""
            var rec = data.getItem('record');
            var conf = rec.getItem('data');
            genro.bp(true)
            conf.forEach(function(branchNode){
                var v = branchNode.getValue();
                var cols_permisson = v.pop('cols_permisson');
                if(cols_permisson){
                    v.setItem('cols_permisson',PermissionComponent.branchPermissions(cols_permisson));
                }
            });
            """)
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2,border_spacing='3px',fld_disabled=True)
        fb.field('user_group')
        fb.field('username')
        fb.field('pkgid')
        fb.field('tblid')
        self.configDataFrame(bc)

    def configDataFrame(self,bc):
        frame = bc.framePane(frameCode='configData',region='center')
        bar = frame.top.slotToolbar('*,mb,*',nodeId='config_controller')
        baseCode ='__base__'
        bar.data('.currpath','#config_controller.record.data.__base__')
        bar.dataFormula('.currpath',"this.absDatapath('.record.data.'+branch || baseCode)",branch='^.branch',
                        baseCode=baseCode)
        bar.dataFormula('.colsgrid_storepath',"this.absDatapath('.record.data.'+branch || baseCode) +'.cols_permisson';",branch='^.branch',
                        baseCode=baseCode)


        bar.mb.multiButton(value='^.branch',items='^.record.$databranches')
        bc = frame.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='^#config_controller.currpath').formbuilder(cols=2,border_spacing='3px')
        fb.remoteSelect(value='^.qtree',lbl='Fields Tree (quick)',auxColumns='code,description',
                        method=self.db.table('adm.user_config').getCustomCodes,
                        condition_tbl='=#FORM.record.tblid',
                        condition_item_type='QTREE',
                        hasDownArrow=True)
        fb.remoteSelect(value='^.ftree',lbl='Fields Tree (full)',auxColumns='code,description',
                        method=self.db.table('adm.user_config').getCustomCodes,
                        condition_tbl='=#FORM.record.tblid',
                        condition_item_type='FTREE',
                        hasDownArrow=True)
        fb.checkBoxText(value='^.tbl_permission',values='hidden,readonly,/,ins,upd,del',cols=3,
                        lbl='Permissions',colspan=2)
        
        sc = bc.stackContainer(region='center')
        bc.dataController("sc.switchPage(tblid?1:0);",sc=sc.js_widget,tblid='^#FORM.record.tblid')
        self.columnsPermissionGrid(sc)

    def struct_permissiongrid(self,struct):
        r = struct.view().rows()
        r.cell('colname',name='Column',width='22em')
        r.checkboxcell('readonly',threestate=True,name='RO')
        r.checkboxcell('forbidden',threestate=True,name='NO')
        r.cell('status',name='Status',width='12em',
            _customGetter="""function(row){
                var result = [];
                var v,inherited;
                ['forbidden','readonly'].forEach(function(c){
                    inherited = false;
                    v = row[c];
                    if(v===null){
                        v=row[c+'_inherited'];
                        inherited=true;
                    }
                    if(v){
                        result.push(inherited?'<span class="dimmed">'+c+'</span>':c)
                    }
                });
                return result.join(',');
            }""")

    def columnsPermissionGrid(self,sc):
        sc.contentPane().div('Choose table')
        bc = sc.borderContainer()
        bc.contentPane(region='left',width='50%').bagGrid(datapath='#FORM.fields_grid',title='Fields',
                                                            struct=self.struct_permissiongrid,
                                                            storepath='^#config_controller.colsgrid_storepath',
                                                            pbl_classes=True,margin='2px',
                                                            addrow=False,delrow=False,datamode='attr')


    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        record['$databranches'] = self.getDataBranches(record['tblid'])
        if not record['tblid']:
            return
        tblobj =  self.db.table(record['tblid'])
        cols_permisson_base = Bag()
        for c in tblobj.columns.keys():
            cols_permisson_base.setItem(c,None,colname=c)

        f = self.query(where="""($pkgid IS NULL OR $pkgid=:pkg) AND
                                    ($tblid IS NULL OR $tblid=:tbl) AND
                                    ($user_group IS NULL OR $user_group=:user_group) AND 
                                    ($username IS NULL OR $username=:user)
                                  """,pkg=record['pkgid'],tbl=record['tblid'],
                                      user_group=record['user_group'],
                                      user=record['username'],
                                  order_by='$rank ASC',columns="""$data""",addPkeyColumn=False).fetch()

        for branch in record['$databranches'].keys():
            
            
    
            for b in :
                


    def getDataBranches(self,tbl=None):
        result = Bag()
        result.setItem('__base__',None,code='__base__',caption='Base')
        if not tbl:
            return result
        tblobj = self.db.table(tbl)
        branch_field = tblobj.attributes.get('branch_field')
        if not branch_field:
            return result
        branches = tblobj.column(branch_field).attributes.get('values')
        for c in branches.split(','):
            code,caption = c.split(':')
            result.setItem(code.replace('.','_'),None,code=code,caption=caption)
        return result

    def th_top_custom(self,top):
        self.newRuleButton(top.bar.replaceSlots('form_add','newrule'))

    def th_options(self):
        return dict(dialog_parentRatio=.9)


