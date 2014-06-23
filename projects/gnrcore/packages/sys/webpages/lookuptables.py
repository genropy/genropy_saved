# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import boolean

class GnrCustomWebPage(object):
    py_requires='public:Public,th/th:TableHandler'
    
    def main(self,root,th_public=None,**kwargs):
        callArgs = self.getCallArgs('th_pkg','th_table')
        public = boolean(th_public) if th_public else True
        root.attributes['datapath'] = 'main'
        pkg = callArgs.get('th_pkg')
        tbl = callArgs.get('th_table')
        fixeed_table =False
        title = '!!Lookup Tables' 
        if pkg:
            title = '%s' %self.db.model.package(pkg).attributes.get('name_long')
            if tbl:
                tblobj = self.db.table('%(th_pkg)s.%(th_table)s' %callArgs)
                title = tblobj.name_plural or tblobj.name_long
        if public:
            root = root.rootContentPane(title=title,**kwargs)
        frame = root.framePane(nodeId='lookup_root')

        if not tbl:
            bar = frame.top.slotToolbar('10,tblfb,*')
            fb = bar.tblfb.formbuilder(cols=2,border_spacing='3px')
            fb.data('.package',pkg)
            fb.dataRemote('.packages',self.packageMenu)
            fb.dataRemote('.tables',self.tableMenu,currPkg='^.package')
            width='30em'
            if not pkg:
                fb.filteringSelect(value='^.package',lbl='!!Package',storepath='.packages',storeid='.code', width=width,
                                storecaption='.description',validate_onAccept='SET .table=null;')
            fb.filteringSelect(value='^.table',lbl='!!Tables',storepath='.tables',storeid='.code', width=width,
                                storecaption='.description',disabled='^.package?=!#v')
        else:
            root.dataFormula('.table','tbl',tbl='%(th_pkg)s.%(th_table)s' %callArgs,_onStart=1)
            fixeed_table = True
        root.dataController("""
                SET main.current_table=table;""",table='^main.table',status='=main.mainth.view.grid.status')
        frame.center.contentPane().remote(self.remoteTh,table='^main.current_table',fixeed_table=fixeed_table,_onRemote='FIRE main.load_data;')

    def lookupTablesDefaultStruct(self,struct):
        r = struct.view().rows()
        for k,v in struct.tblobj.model.columns.items():
            attr = v.attributes
            if attr.get('counter'):
                r.fieldcell(k,hidden=True,counter=True)
            elif not (attr.get('_sysfield') or attr.get('dtype') == 'X'):
                r.fieldcell(k,edit=attr['cell_edit'] if 'cell_edit' in attr else True)

    @public_method
    def remoteTh(self,pane,table=None,fixeed_table=None):
        pane.data('.mainth',Bag())
        if not table:
            pane.div('!!Select a table from the popup menu',margin_left='5em',margin_top='5px', color='#8a898a',text_align='center',font_size='large')
        else:
            saveButton = not fixeed_table
            semaphore = not fixeed_table
            tblobj= self.db.table(table)
            th = pane.inlineTableHandler(table=table,viewResource='LookupView',datapath='.mainth',autoSave=False,saveButton=saveButton,semaphore=semaphore,
                                    nodeId='mainth',configurable='*',
                                    view_structCb=self.lookupTablesDefaultStruct,condition_loaddata='^main.load_data',
                                    grid_selfDragRows=tblobj.attributes.get('counter'))
            if fixeed_table:
                bar = th.view.bottom.slotBar('10,revertbtn,*,cancel,savebtn,10',margin_bottom='2px',_class='slotbar_dialog_footer')
                bar.revertbtn.slotButton('!!Revert',action='FIRE main.load_data;',disabled='==status!="changed"',status='^.grid.editor.status')
                bar.cancel.slotButton('!!Cancel',action='genro.nodeById("lookup_root").publish("lookup_cancel");')
                bar.savebtn.slotButton('!!Save',iconClass='editGrid_semaphore',publish='saveChangedRows',command='save',
                               disabled='==status!="changed"',status='^.grid.editor.status',showLabel=True)  
                th.view.grid.attributes.update(selfsubscribe_savedRows='genro.nodeById("lookup_root").publish("lookup_cancel");')
          


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
