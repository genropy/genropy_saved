# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-03.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method

class THPicker(BaseComponent):
    @struct_method
    def pk_palettePicker(self,pane,grid=None,table=None,relation_field=None,paletteCode=None,
                         viewResource=None,searchOn=True,
                         title=None,autoInsert=True,dockButton=True,**kwargs):
        one=None
        many=relation_field
        if grid:
            maintable = grid.getInheritedAttributes()['table']
            if not table:
                tblobj = self.db.table(maintable).column(many).relatedTable().dbtable
                table = tblobj.fullname
            formNode = pane.parentNode.attributeOwnerNode('formId')
            if formNode:
                formtblobj = self.db.table(formNode.attr.get('table'))
                oneJoiner = formtblobj.model.getJoiner(maintable)
                one = oneJoiner.get('many_relation').split('.')[-1]                
        elif table:
            tblobj = self.db.table(table)
        paletteCode = paletteCode or '%s_picker' %table.replace('.','_')
        title = title or tblobj.name_long
        htable = False
        if hasattr(tblobj,'htableFields'):
            htable = True
            self.mixinComponent('gnrcomponents/htablehandler:HTableHandlerBase')
            palette = pane.paletteTree(paletteCode=paletteCode,dockButton=dockButton,title=title,
                            tree_dragTags=paletteCode,searchOn=searchOn).htableStore(table=table)
        else:
            try:
                resource = self._th_getResClass(table=table,resourceName=viewResource,defaultClass='ViewPicker')()
                struct=resource.th_struct
                sortedBy = getattr(resource,'th_order')
                if sortedBy:
                    sortedBy = sortedBy()
            except:
                if tblobj.attributes.get('caption_field'):
                    def struct(struct):
                        r = struct.view().rows()
                        r.fieldcell(tblobj.attributes['caption_field'], name=tblobj.name_long, width='100%')
                    sortedBy = tblobj.attributes.get('caption_field')
            palette = pane.paletteGrid(paletteCode=paletteCode,struct=struct,dockButton=dockButton,
                            title=title,searchOn=searchOn,grid_filteringGrid=grid,
                             grid_filteringColumn='_pkey:%s' %many).selectionStore(table=table,sortedBy=sortedBy or 'pkey')
        if grid:
            grid.dragAndDrop(paletteCode)
            if autoInsert:
                if htable:
                    method = getattr(tblobj,'insertPicker',self._th_insertPickerTree)
                else:
                    method = getattr(tblobj,'insertPicker',self._th_insertPickerGrid)
            
                grid.dataController("""
                    var kw = {dropPkey:mainpkey,tbl:tbl,one:one,many:many};
                    if(htable){
                        kw.dragPkey = data['pkey'];
                    }else{
                        var pkeys = [];
                        dojo.forEach(data,function(n){pkeys.push(n['_pkey'])});
                        kw.dragPkeys = pkeys;
                    }
                    genro.serverCall(rpcmethod,kw,function(){},null,'POST');

                """,data='^.dropped_%s' %paletteCode,mainpkey='=#FORM.pkey',_if='mainpkey',
                        rpcmethod=method,htable=htable,tbl=maintable,one=one,many=many)
                    
        return palette

    @struct_method
    def th_slotbar_thpicker(self,pane,relation_field=None,**kwargs):
        view = pane.parent.parent.parent    
        grid = view.grid    
        return pane.palettePicker(grid,relation_field=relation_field,**kwargs)

    @public_method
    def _th_insertPickerGrid(self,dragPkeys=None,dropPkey=None,tbl=None,one=None,many=None,**kwargs):
        tblobj = self.db.table(tbl)
        commit = False
        records = tblobj.query(where='$%s=:p' %one,p=dropPkey).fetchAsDict(many)
        for fkey in dragPkeys:
            if not fkey in records:
                commit = True
                tblobj.insert({one:dropPkey,many:fkey})
        if commit:
            self.db.commit()
        
    @public_method
    def _th_insertPickerTree(self,dragPkey=None,dropPkey=None,tbl=None,one=None,many=None,**kwargs):
        tblobj = self.db.table(tbl)
        if not tblobj.checkDuplicate(**{one:dropPkey,many:dropPkey}):
            tblobj.insert({one:dropPkey,many:dragPkey})
            self.db.commit()
    