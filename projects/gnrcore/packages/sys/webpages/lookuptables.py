# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='public:Public,th/th:TableHandler'
    
    def main(self,root,**kwargs):
        root = root.rootContentPane(title='!!Tables manager',datapath='main',**kwargs)
        frame = root.framePane()
        callArgs = self.getCallArgs('th_pkg','th_table')
        pkg = callArgs.get('th_pkg')
        tbl = callArgs.get('th_table')
        if not tbl:
            bar = frame.top.slotToolbar('10,tblfb,*')
            fb = bar.tblfb.formbuilder(cols=2,border_spacing='3px')
            fb.data('.package',pkg)
            fb.dataRemote('.packages',self.packageMenu)
            fb.dataRemote('.tables',self.tableMenu,currPkg='^.package')
            if not pkg:
                fb.filteringSelect(value='^.package',lbl='!!Package',storepath='.packages',storeid='.code', 
                                storecaption='.description',validate_onAccept='SET .table=null;')
            fb.filteringSelect(value='^.table',lbl='!!Tables',storepath='.tables',storeid='.code', storecaption='.description',visible='^.package')
        else:
            root.dataFormula('.table','tbl',tbl='%(th_pkg)s.%(th_table)s' %callArgs,_onStart=1)
        frame.center.contentPane().remote(self.remoteTh,table='^.table')

    def lookupTablesDefaultStruct(self,struct):
        r = struct.view().rows()
        for k,v in struct.tblobj.model.columns.items():
            attr = v.attributes
            if not (attr.get('_sysfield') or attr.get('dtype') == 'X'):
                r.fieldcell(k,edit=attr['cell_edit'] if 'cell_edit' in attr else True)

    @public_method
    def remoteTh(self,pane,table=None):
        if not table:
            pane.div('!!Missing table')
        else:
            pane.data('.mainth',Bag())
            pane.inlineTableHandler(table=table,viewResource='LookupView',datapath='.mainth',
                                    view_structCb=self.lookupTablesDefaultStruct,condition__onBuilt=True)


    def getLookupTable(self,pkg=None):
        result = []
        for tbl in self.db.model.package(pkg).tables.values():
            if tbl.attributes.get('lookup'):
                result.append(tbl)
        return result

    @public_method
    def packageMenu(self):
        result = Bag()
        for pkg in self.application.packages:
            attr = pkg.attr
            if attr.get('_syspackage'):
                continue
            lookup_tables = self.getLookupTable(pkg.label)
            if lookup_tables:
                result.setItem(pkg.label,Bag(code=pkg.label,description=pkg.value.attributes.get('name_long') or pkg))
        return result

    @public_method
    def tableMenu(self,currPkg=None):
        if not currPkg:
            return
        lookup_tables = self.getLookupTable(pkg=currPkg)
        result = Bag()
        for t in lookup_tables:
            result.setItem(t.fullname.replace('.','_'),Bag(code=t.fullname,description=t.name_long))
        return result
