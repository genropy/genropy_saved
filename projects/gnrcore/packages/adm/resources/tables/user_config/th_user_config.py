#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group',hidden='^#mainpars.user_group',width='6em')
        r.fieldcell('user_id',hidden='^#mainpars.user_id',width='7em')
        r.fieldcell('pkgid',hidden='^#mainpars.pkgid',width='4em')
        r.fieldcell('tblid',hidden='^#mainpars.tblid',width='8em')
        r.fieldcell('data')

    def th_hiddencolumns(self):
        return '$rank'

    def th_order(self):
        return 'rank:a'

    def th_condition(self):
        return dict(condition="""(:ugroup IS NULL OR $user_group=:ugroup) AND
                                (:uid IS NULL OR $user_id=:uid) AND
                                (:pkginfo IS NULL OR $pkgid=:pkginfo) AND
                                (:tblinfo IS NULL OR $tblid=:tblinfo)
                            """,condition_ugroup='^#mainpars.user_group',
                                 condition_uid='^#mainpars.user_id',
                                 condition_tblinfo='^#mainpars.tblid',
                                 condition_pkginfo='^#mainpars.pkgid'
                                 )

class Form(BaseComponent):
    def th_form(self,form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2,border_spacing='3px')
        fb.field('user_group')
        fb.field('user_id',condition='$group_code IS NULL OR $group_code=:user_group',
                condition_user_group='=.user_group')
        fb.field('pkgid',hasDownArrow=True)
        fb.field('tblid',hasDownArrow=True,condition='$pkgid=:pkgid',
                condition_pkgid='=.pkgid',disabled='^.pkgid?=!#v')
        self.configDataFrame(bc)

    def configDataFrame(self,bc):
        frame = bc.framePane(frameCode='configData',region='center')
        bar = frame.top.slotToolbar('*,mb,*',nodeId='config_controller')
        baseCode ='__base__'
        bar.data('.currpath','#config_controller.record.__base__')
        bar.dataFormula('.currpath',"this.absDatapath('.record.'+branch || baseCode)",branch='^.branch',
                        baseCode=baseCode)
        bar.dataFormula('.readonlyFieldsStore',"this.absDatapath('.record.'+branch || baseCode) +'.readonly_fields';",branch='^.branch',
                        baseCode=baseCode)
        bar.dataFormula('.forbiddenFieldsStore',"this.absDatapath('.record.'+branch || baseCode) +'.forbidden_fields'; ",branch='^.branch',
                        baseCode=baseCode)
        bar.mb.multiButton(value='^.branch',items='^.databranches')
        bar.dataRpc('.databranches',self.getDataBranches,tbl='^.record.tblid',baseCode=baseCode,baseCaption='!!Base',
                    _if='tbl',
                    _else="""
                    var result = new gnr.GnrBag();
                    result.setItem('__base__',null,{code:baseCode,caption:baseCaption});
                    SET .branch = baseCode;
                    return result;
                    """,_onResult="SET .branch = kwargs.baseCode")
        
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
        self.columnsPermissionGrids(sc)

    def struct_permissiongrid(self,struct):
        r = struct.view().rows()
        r.checkboxcolumn('permission',threestate=True,name=' ')
        r.cell('colname',name='Column',width='100%')


    def columnsPermissionGrids(self,sc):
        sc.contentPane().div('Choose table')
        bc = sc.borderContainer()
        bc.contentPane(region='left',width='50%').bagGrid(datapath='#FORM.readonlycols_grid',title='Read only fields',
                                                            struct=self.struct_permissiongrid,
                                                            storepath='^#config_controller.readonlyFieldsStore',
                                                            pbl_classes='*',margin='2px',addrow=False,delrow=False)
        bc.contentPane(region='center').bagGrid(datapath='#FORM.forbiddencols_grid',title='Forbidden fields',
                                                            struct=self.struct_permissiongrid,
                                                            storepath='^#config_controller.forbiddenFieldsStore',
                                                            pbl_classes='*',margin='2px',addrow=False,delrow=False)

    @public_method
    def getDataBranches(self,tbl=None,baseCode=None,baseCaption=None):
        tblobj = self.db.table(tbl)
        branch_field = tblobj.attributes.get('branch_field')
        result = Bag()
        result.setItem('__base__',None,code=baseCode,caption=baseCaption)
        if not branch_field:
            return result
        branches = tblobj.column(branch_field).attributes.get('values')
        for c in branches.split(','):
            code,caption = c.split(':')
            result.setItem(code.replace('.','_'),None,code=code,caption=caption)
        return result

    def th_options(self):
        return dict(dialog_parentRatio=.9)


