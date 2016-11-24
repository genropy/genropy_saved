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
        r.fieldcell('data',width='30em')

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
class ViewFromUser(View):
    def th_condition(self):
        return dict(condition="""($user_group IS NULL OR $user_group=:ugroup) AND
                                ($username IS NULL OR $username=:uid)
                            """,condition_ugroup='^#FORM.record.group_code',
                                 condition_uid='^#FORM.record.username')
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group',width='6em')
        r.fieldcell('pkgid',width='4em')
        r.fieldcell('tblid',width='8em')
        r.fieldcell('data',width='30em')

class Form(BaseComponent):
    js_requires = 'adm_configurator'
    def th_form(self,form):
        form.store.handler('save',onSaving="""
            var rec = data.getItem('record');
            var conf = rec.getItem('data');
            var cols_permission = conf.pop('cols_permission');
            if(cols_permission){
                conf.setItem('cols_permission',PermissionComponent.colsPermissionsData(cols_permission));
            }
            """)
        form.css('.dojoxGrid-row.virtualCol',"color:green;")
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2,border_spacing='3px')
        fb.field('user_group',fld_disabled=True)
        fb.field('username',fld_disabled=True,tag='textbox')
        fb.field('pkgid',fld_disabled=True)
        fb.field('tblid',fld_disabled=True)

        fb.remoteSelect(value='^.data.qtree',lbl='Fields Tree (quick)',auxColumns='code,description',
                        method=self.db.table('adm.user_config').getCustomCodes,
                        condition_tbl='=#FORM.record.tblid',
                        condition_item_type='QTREE',
                        hasDownArrow=True)
        fb.remoteSelect(value='^.data.ftree',lbl='Fields Tree (full)',auxColumns='code,description',
                        method=self.db.table('adm.user_config').getCustomCodes,
                        condition_tbl='=#FORM.record.tblid',
                        condition_item_type='FTREE',
                        hasDownArrow=True)
        fb.checkBoxText(value='^.data.tbl_permission',values='hidden,readonly,/,ins,upd,del',cols=3,
                        lbl='Permissions',colspan=2)
        sc = bc.stackContainer(region='center')
        bc.dataController("sc.switchPage(tblid?1:0);",sc=sc.js_widget,tblid='^#FORM.record.tblid')
        sc.contentPane()
        frame = sc.contentPane().bagGrid(frameCode='cols_permission',datapath='#FORM.fields_grid',title='Fields',
                                                            struct=self.struct_permissiongrid,
                                                            storepath='#FORM.record.data.cols_permission',
                                                            pbl_classes=True,margin='2px',
                                                            addrow=False,delrow=False,datamode='attr')
        bar = frame.top.bar.replaceSlots('#','#,colspicker,5')
        palette = bar.colspicker.paletteGrid(paletteCode='colspicker',
                                            struct=self.colspicker_struct,dockButton=True,
                                            grid_filteringGrid=frame.grid.js_sourceNode(),
                                            grid_filteringColumn='_pkey:colname'
                                            )
        palette.bagStore(storepath='#FORM.record.$current_cols',storeType='AttributesBagRows')
        frame.grid.dragAndDrop('colspicker')
        frame.grid.dataController("""
            data.forEach(function(r){
                    permissions_store.setItem(r.colname,null,{colname:r.colname});
                });
            """,data='^.dropped_colspicker',_if='data',
            permissions_store='=#FORM.record.data.cols_permission')

    def colspicker_struct(self,struct):
        r = struct.view().rows()
        r.cell('colname',name='Column',width='22em')
        r.cell('datatype',name='Dtype',width='7em')

    def struct_permissiongrid(self,struct):
        r = struct.view().rows()
        r.cell('colname',name='Column',width='22em')
        r.checkboxcell('readonly',threestate=True,name='Readonly')
        r.checkboxcell('forbidden',threestate=True,name='Forbidden')
        r.cell('status',name='Status',width='12em',
            _customGetter="""function(row){
                var result = [];
                var v,inherited;
                ['forbidden','readonly'].forEach(function(c){
                    inherited = false;
                    v = row[c];
                    if(isNullOrBlank(v)){
                        v=row[c+'_inherited'];
                        inherited=true;
                    }
                    if(v){
                        result.push(inherited?'<span class="dimmed">'+c+'</span>':c)
                    }
                });
                return result.join(',');
            }""")


    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if record['tblid']:
            current_full_data = self.db.table('adm.user_config').getInfoBag(pkg=record['pkgid'],tbl=record['tblid'],
                                                                            user=record['username'],
                                                                            user_group=record['user_group'],
                                                                            _editMode=True)
            record['data.cols_permission'] = current_full_data['cols_permission']
            record['$current_cols'] = self.colsPickerStore(record['tblid'])

    def th_top_custom(self,top):
        self.newRuleButton(top.bar.replaceSlots('form_add','newrule'))

    def th_options(self):
        return dict(dialog_parentRatio=.9)


    @public_method
    def colsPickerStore(self,table=None):
        tblobj = self.db.table(table)
        result = Bag()
        for field,colobj in tblobj.model.columns.items():
            colattr = colobj.attributes
            result.setItem(field,None,colname=field,name_long=colattr.get('name_long'),
                                    datatype=colattr.get('dtype','T'),_pkey=field)

        for field,colobj in tblobj.model.virtual_columns.items():
            colattr = colobj.attributes
            result.setItem(field,None,colname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T'),_customClasses='virtualCol',_pkey=field)

        return result

