# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-03.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrdict import dictExtract
class THPicker(BaseComponent):
    @struct_method
    def pk_palettePicker(self,pane,grid=None,table=None,relation_field=None,paletteCode=None,
                         viewResource=None,searchOn=True,multiSelect=True,
                         title=None,autoInsert=None,dockButton=True,picker_kwargs=None,
                         height=None,width=None,**kwargs):
        
        one = False
        picker_kwargs = picker_kwargs or dict()
        condition=picker_kwargs.pop('condition',None)
        condition_kwargs = dictExtract(picker_kwargs,'condition_',pop=True,slice_prefix=True)
        
        many = relation_field or picker_kwargs.get('relation_field',None)
        table = table or picker_kwargs.get('table',None)
        height = height or picker_kwargs.get('height')
        width = width or picker_kwargs.get('width')
        if autoInsert is None:
            autoInsert = picker_kwargs.get('autoInsert',True)
        title = title or picker_kwargs.get('title')
        viewResource = viewResource or picker_kwargs.get('viewResource')
        if viewResource is True:
            viewResource = ':ViewPicker'
        searchOn = searchOn or picker_kwargs.get('searchOn')
        paletteCode = paletteCode or picker_kwargs.get('paletteCode')
        maintable = None
        if grid:
            maintable = grid.getInheritedAttributes()['table']
            if not table:
                tblobj = self.db.table(maintable).column(many).relatedTable().dbtable
                table = tblobj.fullname  
            else:
                tblobj = self.db.table(table) 
        elif table:
            tblobj = self.db.table(table)
        paletteCode = paletteCode or '%s_picker' %table.replace('.','_')
        title = title or tblobj.name_long
        oldtreePicker = hasattr(tblobj,'htableFields') and not viewResource
        treepicker = tblobj.attributes.get('hierarchical') and not viewResource
        if oldtreePicker:
            self.mixinComponent('gnrcomponents/htablehandler:HTableHandlerBase')
            palette = pane.paletteTree(paletteCode=paletteCode,dockButton=dockButton,title=title,
                            tree_dragTags=paletteCode,searchOn=searchOn,width=width,height=height).htableStore(table=table)
        elif treepicker:
            palette = pane.paletteTree(paletteCode=paletteCode,dockButton=dockButton,title=title,
                            tree_dragTags=paletteCode,searchOn=searchOn,width=width,height=height).htableViewStore(table=table)
        elif viewResource:
            palette = pane.palettePane(paletteCode=paletteCode,dockButton=dockButton,
                                        title=title,width=width,height=height)
            paletteth = palette.plainTableHandler(table=table,viewResource=viewResource,
                                                    grid_onDrag='dragValues["%s"]=dragValues.gridrow.rowset;' %paletteCode,
                                                    grid_multiSelect=multiSelect,
                                                    title=title,searchOn=searchOn,configurable=False,
                                                  childname='picker_tablehandler')
            if condition:
                paletteth.view.store.attributes.update(where=condition,**condition_kwargs)
            if not condition_kwargs:
                paletteth.view.store.attributes.update(_onStart=True)
            if grid:
                paletteth.view.grid.attributes.update(filteringGrid=grid.js_sourceNode(),filteringColumn='_pkey:%s' %many)
        elif tblobj.attributes.get('caption_field'):
            def struct(struct):
                r = struct.view().rows()
                r.fieldcell(tblobj.attributes['caption_field'], name=tblobj.name_long, width='100%')
            sortedBy = tblobj.attributes.get('caption_field')
            paletteGridKwargs = dict(paletteCode=paletteCode,struct=struct,dockButton=dockButton,
                            grid_multiSelect=multiSelect,
                            title=title,searchOn=searchOn,
                            width=width,height=height)
            if grid:
                paletteGridKwargs['grid_filteringGrid']=grid
                paletteGridKwargs['grid_filteringColumn'] = '_pkey:%s' %many
            condition_kwargs.setdefault('_onStart',True)
            palette = pane.paletteGrid(**paletteGridKwargs).selectionStore(table=table,sortedBy=sortedBy or 'pkey',condition=condition,**condition_kwargs)
        if grid:
            grid.dragAndDrop(paletteCode)
            if autoInsert:
                method = getattr(tblobj,'insertPicker',self._th_insertPicker)
                formNode = pane.parentNode.attributeOwnerNode('formId')
                if formNode:
                    formtblobj = self.db.table(formNode.attr.get('table'))
                    oneJoiner = formtblobj.model.getJoiner(maintable)
                    one = oneJoiner.get('many_relation').split('.')[-1]  
                grid.dataController("""
                    var kw = {dropPkey:mainpkey,tbl:tbl,one:one,many:many};
                    if(treepicker){
                        kw.dragPkeys = [data['pkey']];
                    }else{
                        var pkeys = [];
                        dojo.forEach(data,function(n){pkeys.push(n['_pkey'])});
                        kw.dragPkeys = pkeys;
                    }
                    kw['_sourceNode'] = this;
                    if(grid.gridEditor && grid.gridEditor.editorPars){
                        var rows = [];
                        dojo.forEach(kw.dragPkeys,function(fkey){
                            var r = {};
                            r[many] = fkey;
                            rows.push(r);
                        });
                        grid.gridEditor.addNewRows(rows);
                    }else if(mainpkey){
                        genro.serverCall(rpcmethod,kw,function(){},null,'POST');
                    }

                """,data='^.dropped_%s' %paletteCode,mainpkey='=#FORM.pkey',
                        rpcmethod=method,treepicker=oldtreePicker or treepicker or False,tbl=maintable,
                        one=one,many=many,grid=grid.js_widget)  
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
        for fkey in dragPkeys:
            commit = True
            tblobj.insert({one:dropPkey,many:fkey})
        if commit:
            self.db.commit()

    @struct_method
    def th_slotbar_addrowmenu(self,pane,parameters=None,**kwargs):
        view = pane.parent.parent.parent    
        grid = view.grid  
        many = parameters['relation_field']
        condition = parameters.get('condition')
        condition_kwargs = dictExtract(parameters,'condition_')
        unique = parameters.get('unique',False)
        cacheTime = parameters.get('cacheTime',-1)
        one = False
        maintable = pane.getInheritedAttributes()['table']
        relation_tblobj = self.db.table(maintable).column(many).relatedTable().dbtable

        formNode = view.parentNode.attributeOwnerNode('formId')
        if formNode:
            formtblobj = self.db.table(formNode.attr.get('table'))
            oneJoiner = formtblobj.model.getJoiner(maintable)
            one = oneJoiner.get('many_relation').split('.')[-1] 

        hiddenItemCb = None
        if unique:
            hiddenItemCb="""var excludelist = genro.wdgById('%s').getColumnValues('%s')
                              return (dojo.indexOf(excludelist,item.pkey)>=0)
                              """ %(grid.attributes.get('nodeId'),many)
        pane.menudiv(storepath='.picker_menu',iconClass='add_row',tip='!!Add',
                        action='FIRE .grid.addrowmenu_%s = $1.pkey' %many,
                        hiddenItemCb=hiddenItemCb,parentForm=True)

        pane.dataRemote('.picker_menu',self.th_addmenu_menucontent,dbtable=relation_tblobj.fullname,many=many,one=one,
                        formpkey='=#FORM.pkey',cacheTime=cacheTime,condition=condition,condition_kwargs=condition_kwargs)
        method = getattr(relation_tblobj,'insertMenu',self._th_insertPicker)
        grid.dataController("""
                    var kw = {dropPkey:mainpkey,tbl:tbl,one:one,many:many};
                    kw.dragPkeys = [fkey];
                    kw['_sourceNode'] = this;
                    if(grid.gridEditor && grid.gridEditor.editorPars){
                        var rows = [];
                        dojo.forEach(kw.dragPkeys,function(fkey){
                            var r = {};
                            r[many] = fkey;
                            rows.push(r);
                        });
                        grid.gridEditor.addNewRows(rows);
                    }else if(mainpkey){
                        genro.serverCall(rpcmethod,kw,function(){},null,'POST');
                    }
                """,fkey='^.addrowmenu_%s' %many ,mainpkey='=#FORM.pkey',
                        rpcmethod=method,tbl=maintable,
                        one=one,many=many,grid=grid.js_widget)  

    @public_method
    def th_addmenu_menucontent(self,dbtable=None,condition=None,condition_kwargs=None,**kwargs):
        result = Bag()
        tblobj = self.db.table(dbtable)
        caption_field = tblobj.attributes['caption_field']
        condition_kwargs = dict([(str(k),v) for k,v in condition_kwargs.items()]) #fix unicode
        fetch = tblobj.query(columns='*,$%s' %(caption_field),where=condition,**condition_kwargs).fetch()
        for i,r in enumerate(fetch):
            result.setItem('r_%i' %i,None,caption=r[caption_field],pkey=r['pkey'])
        return result

    