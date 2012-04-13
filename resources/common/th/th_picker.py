# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-03.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent,GnrMissingResourceException
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrdict import dictExtract
class THPicker(BaseComponent):
    @struct_method
    def pk_palettePicker(self,pane,grid=None,table=None,relation_field=None,paletteCode=None,
                         viewResource=None,searchOn=True,
                         title=None,autoInsert=True,dockButton=True,picker_kwargs=None,
                         height=None,width=None,**kwargs):
        
        one=False
        condition=picker_kwargs.pop('condition',None)
        condition_kwargs=dictExtract(picker_kwargs,'condition_',pop=True,slice_prefix=True)
        
        many = relation_field or picker_kwargs.get('relation_field',None)
        height = height or picker_kwargs.get('height')
        width = width or picker_kwargs.get('height')
        autoInsert = autoInsert or picker_kwargs.get('autoInsert')
        title = title or picker_kwargs.get('title')
        viewResource = viewResource or picker_kwargs.get('viewResource')
        searchOn = searchOn or picker_kwargs.get('searchOn')
        paletteCode = paletteCode or picker_kwargs.get('paletteCode')
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
                            tree_dragTags=paletteCode,searchOn=searchOn,width=width,height=height).htableStore(table=table)
        else:
            try:
                resource = self._th_getResClass(table=table,resourceName=viewResource,defaultClass='ViewPicker')()
                struct=resource.th_struct
                sortedBy = getattr(resource,'th_order',None)
                if sortedBy:
                    sortedBy = sortedBy()
            except GnrMissingResourceException:
                if tblobj.attributes.get('caption_field'):
                    def struct(struct):
                        r = struct.view().rows()
                        r.fieldcell(tblobj.attributes['caption_field'], name=tblobj.name_long, width='100%')
                    sortedBy = tblobj.attributes.get('caption_field')


            palette = pane.paletteGrid(paletteCode=paletteCode,struct=struct,dockButton=dockButton,
                            title=title,searchOn=searchOn,grid_filteringGrid=grid,width=width,height=height,
                             grid_filteringColumn='_pkey:%s' %many).selectionStore(table=table,sortedBy=sortedBy or 'pkey',condition=condition,**condition_kwargs)
        if grid:
            grid.dragAndDrop(paletteCode)
            if autoInsert:
                method = getattr(tblobj,'insertPicker',self._th_insertPicker)
                grid.dataController("""
                    var kw = {dropPkey:mainpkey,tbl:tbl,one:one,many:many};
                    if(htable){
                        kw.dragPkeys = [data['pkey']];
                    }else{
                        var pkeys = [];
                        dojo.forEach(data,function(n){pkeys.push(n['_pkey'])});
                        kw.dragPkeys = pkeys;
                    }
                    if(grid.gridEditor && grid.gridEditor.editorPars){
                        var rows = [];
                        dojo.forEach(kw.dragPkeys,function(fkey){
                            var r = {};
                            r[many] = fkey;
                            rows.push(r);
                        });
                        grid.gridEditor.addNewRows(rows);
                    }else{
                        genro.serverCall(rpcmethod,kw,function(){},null,'POST');
                    }

                """,data='^.dropped_%s' %paletteCode,mainpkey='=#FORM.pkey',_if='mainpkey',
                        rpcmethod=method,htable=htable,tbl=maintable,one=one,many=many,grid=grid.js_widget)
                    
        return palette

    @struct_method
    def th_slotbar_thpicker(self,pane,relation_field=None,**kwargs):
        view = pane.parent.parent.parent    
        grid = view.grid    
        return pane.palettePicker(grid,relation_field=relation_field,**kwargs)

    @public_method
    def _th_insertPicker(self,dragPkeys=None,dropPkey=None,tbl=None,one=None,many=None,**kwargs):
        tblobj = self.db.table(tbl)
        commit = False
        records = tblobj.query(where='$%s=:p' %one,p=dropPkey).fetchAsDict(many)
        for fkey in dragPkeys:
            if not fkey in records:
                commit = True
                tblobj.insert({one:dropPkey,many:fkey})
        if commit:
            self.db.commit()

    