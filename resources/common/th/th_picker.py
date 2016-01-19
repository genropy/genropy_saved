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
    js_requires='th/th_picker'
    @struct_method
    def pk_palettePicker(self,pane,grid=None,table=None,relation_field=None,paletteCode=None,
                         viewResource=None,searchOn=True,multiSelect=True,
                         title=None,autoInsert=None,dockButton=None,picker_kwargs=None,
                         height=None,width=None,**kwargs):
        
        dockButton = dockButton or dict(parentForm=True,iconClass='iconbox app')
        picker_kwargs = picker_kwargs or dict()
        one = picker_kwargs.get('one',False)
        picker_kwargs.setdefault('uniqueRow',True)
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
                            tree_dragTags=paletteCode,searchOn=searchOn,width=width,height=height,
                            draggableFolders=picker_kwargs.pop('draggableFolders',None)).htableViewStore(table=table)
        elif viewResource:
            palette = pane.palettePane(paletteCode=paletteCode,dockButton=dockButton,
                                        title=title,width=width,height=height)
            paletteth = palette.plainTableHandler(table=table,viewResource=viewResource,
                                                    grid_onDrag='dragValues["%s"]=dragValues.gridrow.rowset;' %paletteCode,
                                                    grid_multiSelect=multiSelect,
                                                    title=title,searchOn=searchOn,configurable=False,
                                                  childname='picker_tablehandler',nodeId='%s_th' %paletteCode)
            if condition:
                paletteth.view.store.attributes.update(where=condition,**condition_kwargs)
            if not condition_kwargs:
                paletteth.view.store.attributes.update(_onStart=True)
            if grid and picker_kwargs.get('uniqueRow'):
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
            if grid and picker_kwargs.get('uniqueRow'):
                paletteGridKwargs['grid_filteringGrid']=grid
                paletteGridKwargs['grid_filteringColumn'] = '_pkey:%s' %many
            condition_kwargs.setdefault('_onStart',True)
            palette = pane.paletteGrid(**paletteGridKwargs).selectionStore(table=table,sortedBy=sortedBy or 'pkey',condition=condition,**condition_kwargs)
        if grid:
            grid.attributes.update(dropTargetCb_picker='return this.form?!this.form.isDisabled():true')
            grid.dragAndDrop(paletteCode)
            if autoInsert:
                method = getattr(tblobj,'insertPicker',self._th_insertPicker)
                formNode = pane.parentNode.attributeOwnerNode('formId')
                if not one and formNode:
                    formtblobj = self.db.table(formNode.attr.get('table'))
                    oneJoiner = formtblobj.model.getJoiner(maintable)
                    one = oneJoiner.get('many_relation').split('.')[-1]  
                grid.dataController("""
                    var kw = {dropPkey:mainpkey,tbl:tbl,one:one,many:many};
                    var cbdef = function(destrow,sourcerow,d){
                        var l = d.split(':');
                        var sfield = l[0];
                        var dfield = l.length==1?l[0]:l[1];
                        destrow[dfield] = sourcerow[sfield];
                    }
                    if(treepicker){
                        kw.dragPkeys = [data['pkey']];
                        if(defaults){
                            var drow = {};
                            kw.dragDefaults = {}
                            defaults.split(',').forEach(function(d){cbdef(drow,data['_record'],d);});
                            kw.dragDefaults[data['pkey']] = drow;
                        }
                    }else{
                        var pkeys = [];
                        var dragDefaults = {};
                        dojo.forEach(data,function(n){
                            pkeys.push(n['_pkey'])
                            if(defaults){
                                var drow = {};
                                defaults.split(',').forEach(function(d){cbdef(drow,n,d);});
                                dragDefaults[n['_pkey']] = drow;
                            }
                            
                        });
                        kw.dragPkeys = pkeys;
                        kw.dragDefaults = dragDefaults;
                    }
                    kw['_sourceNode'] = this;
                    if(grid.gridEditor && grid.gridEditor.editorPars){
                        var rows = [];
                        dojo.forEach(kw.dragPkeys,function(fkey){
                            var r = {};
                            r[many] = fkey;
                            if(kw.dragDefaults){
                                objectUpdate(r,kw.dragDefaults[fkey]);
                            }
                            rows.push(r);
                        });
                        grid.gridEditor.addNewRows(rows);
                    }else if(mainpkey){
                        genro.serverCall(rpcmethod,kw,function(){},null,'POST');
                    }

                """,data='^.dropped_%s' %paletteCode,mainpkey='=#FORM.pkey',
                        rpcmethod=method,treepicker=oldtreePicker or treepicker or False,tbl=maintable,
                        one=one,many=many,grid=grid.js_widget,defaults=picker_kwargs.get('defaults',False))  
        return palette

    @struct_method
    def th_slotbar_thpicker(self,pane,relation_field=None,picker_kwargs=None,**kwargs):
        view = pane.parent.parent.parent    
        grid = view.grid    
        if picker_kwargs.get('structure_field'):
            return pane.paletteStructurePicker(grid,relation_field=relation_field,picker_kwargs=picker_kwargs,**kwargs)
        return pane.palettePicker(grid,relation_field=relation_field,picker_kwargs=picker_kwargs,**kwargs)

    @public_method
    def _th_insertPicker(self,dragPkeys=None,dropPkey=None,tbl=None,one=None,many=None,dragDefaults=None,**kwargs):
        tblobj = self.db.table(tbl)
        commit = False
        for fkey in dragPkeys:
            commit = True
            d = {one:dropPkey,many:fkey}
            r = tblobj.newrecord()
            r.update(d)
            if dragDefaults:
                r.update(dragDefaults[fkey])
            tblobj.insert(r)
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
        loadWithDefault = parameters.get('loadWithDefault')
        one = False
        maintable = pane.getInheritedAttributes()['table']
        relation_tblobj = self.db.table(maintable).column(many).relatedTable().dbtable

        formNode = view.parentNode.attributeOwnerNode('formId')
        if formNode:
            formtblobj = self.db.table(formNode.attr.get('table'))
            oneJoiner = formtblobj.model.getJoiner(maintable)
            if oneJoiner:
                one = oneJoiner.get('many_relation').split('.')[-1] 

        hiddenItemCb = None
        if unique:
            hiddenItemCb="""var excludelist = genro.wdgById('%s').getColumnValues('%s')
                              return (dojo.indexOf(excludelist,item.pkey)>=0)
                              """ %(grid.attributes.get('nodeId'),many)

        if(hasattr(relation_tblobj,'hierarchicalHandler')):
            pane.dataRemote('.picker_menu',relation_tblobj.getHierarchicalData,
                        formpkey='=#FORM.pkey',cacheTime=cacheTime,condition=condition,
                        condition_kwargs=condition_kwargs)
            menupath = '.picker_menu.root'
        else:
            pane.dataRemote('.picker_menu',self.th_addmenu_menucontent,dbtable=relation_tblobj.fullname,many=many,one=one,
                        formpkey='=#FORM.pkey',cacheTime=cacheTime,condition=condition,condition_kwargs=condition_kwargs)
            menupath = '.picker_menu'
        pane.menudiv(storepath=menupath,iconClass='add_row',tip='!!Add',
                        action='FIRE .grid.addrowmenu_%s = $1.pkey' %many,
                        hiddenItemCb=hiddenItemCb,parentForm=True)
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
                        if(loadWithDefault){
                            var default_kw = {};
                            default_kw[many] = fkey;
                            grid.sourceNode.publish('editrow',{pkey:'*newrecord*',default_kw:default_kw});
                        }else{
                            genro.serverCall(rpcmethod,kw,function(){},null,'POST');
                        }
                    }
                """,fkey='^.addrowmenu_%s' %many ,mainpkey='=#FORM.pkey',
                        rpcmethod=method,tbl=maintable,
                        one=one,many=many,grid=grid.js_widget,
                        loadWithDefault=loadWithDefault or False)  

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




    @struct_method
    def pk_paletteStructurePicker(self,pane,grid=None,table=None,relation_field=None,paletteCode=None,
                         viewResource=None,searchOn=True,multiSelect=True,
                         title=None,autoInsert=None,dockButton=True,picker_kwargs=None,
                         height=None,width=None,**kwargs):
        
        structure_field = picker_kwargs.get('structure_field')
        picker_kwargs = picker_kwargs or dict()
        one = picker_kwargs.get('one',False)
        picker_kwargs.setdefault('uniqueRow',True)
        condition=picker_kwargs.pop('condition',None)
        condition_kwargs = dictExtract(picker_kwargs,'condition_',pop=True,slice_prefix=True)
        many = relation_field or picker_kwargs.get('relation_field',None)
        table = table or picker_kwargs.get('table',None)
        height = height or picker_kwargs.get('height','600px')
        width = width or picker_kwargs.get('width','400px')
        if autoInsert is None:
            autoInsert = picker_kwargs.get('autoInsert',True)
        title = title or picker_kwargs.get('title')
        viewResource = viewResource or picker_kwargs.get('viewResource')
        if viewResource is True:
            viewResource = 'ViewPicker'
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

        palette = pane.palettePane(paletteCode=paletteCode,dockButton=dockButton,
                                        title=title,width=width,height=height)
        def struct(struct):
            r = struct.view().rows()
            r.fieldcell(tblobj.attributes['caption_field'], name=tblobj.name_long, width='100%')
        viewResource = viewResource or 'PickerView'
        bc = palette.borderContainer(_anchor=True)
        center = bc.contentPane(region='center')
        paletteth = center.plainTableHandler(table=table,viewResource=viewResource,
                                                grid_onDrag='dragValues["%s"]=dragValues.gridrow.rowset;' %paletteCode,
                                                grid_multiSelect=multiSelect,
                                                view_structCb=struct,
                                                title=title,searchOn=searchOn,configurable=False,
                                              childname='picker_tablehandler',nodeId='%s_th' %paletteCode)
        if structure_field:
            structure_tblobj = tblobj.column(structure_field).relatedTable().dbtable
            top = bc.contentPane(region='top',height=picker_kwargs.get('top_height','50%'),splitter=True,datapath='.structuretree')
            top.tree(storepath='.store',_class='fieldsTree', hideValues=True,
                            draggable=False,
                            selectedLabelClass='selectedTreeNode',
                            labelAttribute='caption',
                            selected_pkey='.tree.pkey',
                            selected_hierarchical_pkey='.tree.hierarchical_pkey',                          
                            selectedPath='.tree.path',  
                            identifier='treeIdentifier',margin='6px',
                        ).htableViewStore(table=structure_tblobj.fullname)

            paletteth.view.store.attributes.update(where = """
                                                        ( (:selected_pkey IS NOT NULL) AND (@%s.hierarchical_pkey ILIKE (:hierarchical_pkey || '%s') )  
                                                            OR ( ($%s IS NULL) AND (:selected_pkey IS NULL) ) )
                                                    """ %(structure_field,'%%',structure_field),
                                  hierarchical_pkey='^#ANCHOR.structuretree.tree.hierarchical_pkey',
                                  selected_pkey='^#ANCHOR.structuretree.tree.pkey',_delay=500)

        if condition:
            paletteth.view.store.attributes.update(where=condition,**condition_kwargs)
        if not condition_kwargs:
            paletteth.view.store.attributes.update(_onStart=True)
        if grid and picker_kwargs.get('uniqueRow'):
            paletteth.view.grid.attributes.update(filteringGrid=grid.js_sourceNode(),filteringColumn='_pkey:%s' %many)
        if grid:
            grid.dragAndDrop(paletteCode)
            if autoInsert:
                method = getattr(tblobj,'insertPicker',self._th_insertPicker)
                formNode = pane.parentNode.attributeOwnerNode('formId')
                if not one and formNode:
                    formtblobj = self.db.table(formNode.attr.get('table'))
                    oneJoiner = formtblobj.model.getJoiner(maintable)
                    one = oneJoiner.get('many_relation').split('.')[-1]  
                grid.dataController("""
                    THPicker.onDropElement(this,data,mainpkey,rpcmethod,treepicker,tbl,one,many,grid,defaults)                    
                """,data='^.dropped_%s' %paletteCode,mainpkey='=#FORM.pkey',
                        rpcmethod=method,treepicker=False,tbl=maintable,
                        one=one,many=many,grid=grid.js_widget,defaults=picker_kwargs.get('defaults',False))  
        return palette

    