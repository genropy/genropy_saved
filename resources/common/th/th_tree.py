# -*- coding: utf-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-09.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method

class HTableTree(BaseComponent):
    js_requires='th/th_tree'
    @extract_kwargs(tree=True)
    @struct_method
    def ht_hdbselect(self,pane,caption_field=None,treeMode=None,folderSelectable=False,cacheTime=None,connectedMenu=None,tree_kwargs=None,**kwargs):
        dbselect = pane.dbselect(**kwargs)
        attr = dbselect.attributes
        dbselect_condition = attr.get('condition')
        dbselect_condition_kwargs = dictExtract(attr,'condition_',slice_prefix=False)
        dbselect_selected_kwargs = dictExtract(attr,'selected_',slice_prefix=False)
        tree_kwargs.update(dbselect_selected_kwargs)
        if not folderSelectable:
            attr['condition'] = '$child_count=0' if not dbselect_condition else ' ( %s ) AND $child_count=0' %dbselect_condition
        attr['hasDownArrow'] = True
        attr['_hdbselect'] = True
        dbselect_nodeId = attr.get('nodeId') or str(id(dbselect))
        connectedMenu = connectedMenu or 'hmenu_%s' %dbselect_nodeId
        currentHMenu = self.workspace.setdefault('hmenu',{})
        if connectedMenu not in currentHMenu:
            tree_kwargs['openOnClick'] = not folderSelectable
            tree_kwargs['selected_pkey'] = kwargs.get('value').replace('^','')
            menupath = 'gnr.htablestores.%s_%s' %(attr['dbtable'],connectedMenu)
            dbselect.treemenu(storepath=menupath,table=attr['dbtable'],condition=dbselect_condition,
                                condition_kwargs=dbselect_condition_kwargs,modifiers='*',
                                caption_field=caption_field,cacheTime=cacheTime,
                                menuId=connectedMenu,dbstore=kwargs.get('_storename'),**tree_kwargs)
            currentHMenu[connectedMenu] = currentHMenu
        attr['connectedMenu'] = connectedMenu

    @struct_method
    def ht_treemenu(self,pane,storepath=None,table=None,condition=None,condition_kwargs=None,cacheTime=None,
                    caption_field=None,dbstore=None,modifiers=None,max_height=None,min_width=None,menuId=None,columns=None,**kwargs):
        selected_kwargs = dictExtract(kwargs,'selected_')
        columns = columns or '*'
        selected_kwargs.pop('pkey',None)
        if selected_kwargs:
            columns = '%s,%s' %(columns,','.join(['$%s' %k for k in selected_kwargs.keys()])) 
        pane.dataRemote(storepath,self.db.table(table).getHierarchicalData,
                        condition=condition,
                        table=table,columns=columns,
                        cacheTime=cacheTime or -1,caption_field=caption_field,dbstore=dbstore,
                        **condition_kwargs)
        menu = pane.menu(modifiers=modifiers,_class='menupane',connectToParent=False,id=menuId,connect_onOpeningPopup="""
                var dbselect =  dijit.getEnclosingWidget(this.widget.originalContextTarget);
                var dbselectNode =  dijit.getEnclosingWidget(this.widget.originalContextTarget).sourceNode;
                var currvalue = dbselect.getValue();
                var tree = this.getChild('treemenu');
                var treeWdg = tree.widget;
                treeWdg.collapseAll();
                var pathToSelect =null;
                if(currvalue){
                    pathToSelect = THTree.fullPathByIdentifier(treeWdg,currvalue);
                }
                treeWdg.setSelectedPath(null,{value:pathToSelect});
            """)
        menuItem = menu.menuItem().div(max_height=max_height or '350px',min_width= min_width or '300px',overflow='auto')
        menuItem.div(padding_top='4px', padding_bottom='4px').tree(storepath='%s.root' %storepath,
                         hideValues=True,autoCollapse=True,excludeRoot=True,
                         labelAttribute='caption',selectedLabelClass='selectedTreeNode',
                         parentMenu=menu,childname='treemenu',
                         _class="branchtree noIcon",**kwargs)
        return menu
        
    @extract_kwargs(related=True)
    @struct_method
    def ht_htableViewStore(self,treeNode,table=None,storepath='.store',caption_field=None,condition=None,caption=None,
                               dbstore=None,root_id=None,columns=None,related_kwargs=None,resolved=False,**kwargs):
        b = Bag()
        tblobj = self.db.table(table)
        caption = caption or tblobj.name_plural
        tree_datapath = treeNode.attributes.get('datapath')
        storeRoot = treeNode.parent #to make it indipendent from tree rebuild
        if tree_datapath and storepath.startswith('.'): #htableViewStore can be used outside componet
            storepath = '%s%s' %(tree_datapath,storepath) #store storepath from the same point of tree
        if condition or related_kwargs.get('condition'):
            storekw = dict(kwargs)
            for k,v in related_kwargs.items():
                storekw['related_%s' %k] = v
            d = storeRoot.dataRpc(None,tblobj.getHierarchicalData,
                        table=table,
                        caption_field=caption_field,
                        condition=condition,
                        childname='store',caption=caption,dbstore=dbstore,
                        columns=columns,related_kwargs=related_kwargs,
                        nodeId='%s_hdata' %table.replace('.','_'),
                        **storekw)
            d.addCallback("""
                var selectedIdentifier;
                if(treeNode.attr.tag.toLocaleLowerCase()=='tree'){ //avoid paletteTree
                    //tree 
                    var selectedNode = treeNode.widget.currentSelectedNode;
                    selectedIdentifier = selectedNode? selectedNode.item.attr.treeIdentifier:''; 
                    treeNode.widget.saveExpanded();
                }
                result = result || new gnr.GnrBag();
                this.setRelativeData(storepath,result);
                if(!selectedIdentifier){
                    return;
                }
                setTimeout(function(){
                    treeNode.widget.restoreExpanded();
                    if(selectedIdentifier){
                        var fullpath = THTree.fullPathByIdentifier(treeNode.widget,selectedIdentifier);
                        treeNode.widget.setSelectedPath(null,{value:fullpath});
                    }
                },1)
                
            """,storepath=storepath,treeNode=treeNode)
            return d
            
        b = tblobj.getHierarchicalData(caption_field=caption_field,dbstore=dbstore,
                                                    related_kwargs=related_kwargs,
                                                    root_id=root_id,columns=columns,resolved=resolved)
        d = storeRoot.data(storepath,b,childname='store',caption=caption,table=table,
                    search_method=self.db.table(table).hierarchicalSearch,
                    search_related_table=related_kwargs.get('table'),
                    search_related_path=related_kwargs.get('path'),
                    search_related_caption_field=related_kwargs.get('caption_field')
                    ) 
        return d

    @public_method    
    def ht_moveHierarchical(self,table=None,pkey=None,into_pkey=None,parent_id=None,into_parent_id=None,modifiers=None):
        tblobj = self.db.table(table)
        if not modifiers:
            into_pkey = into_pkey or None
            tblobj.batchUpdate(dict(parent_id=into_pkey),where='$id=:pkey',pkey=pkey,bagFields=True)
            self.db.commit()
        elif (modifiers == 'Shift' or modifiers == 'Shift,Meta') and (into_parent_id==parent_id) and tblobj.column('_row_count') is not None:
            where='$parent_id=:p_id' if parent_id else '$parent_id IS NULL'
            f = tblobj.query(where=where,p_id=parent_id,for_update=True,order_by='$_row_count',bagFields=True,addPkeyColumn=False).fetch()
            b = Bag([(r['id'],dict(r)) for r in f])
            pref = '>' if modifiers == 'Shift' else '<'
            b.setItem(pkey,b.pop(pkey),_position='%s%s' %(pref,into_pkey))
            for k,r in enumerate(b.values()):
                counter = k+1
                if r['_row_count'] != counter:
                    old_rec = dict(r)
                    r['_row_count'] = counter
                    tblobj.update(r,old_rec)
            self.db.commit()

    @extract_kwargs(condition=dict(slice_prefix=False),related=True,store=True)
    @struct_method
    def ht_hTableTree(self,pane,storepath='.store',table=None,root_id=None,draggable=True,columns=None,
                        caption_field=None,condition=None,caption=None,dbstore=None,condition_kwargs=None,store_kwargs=True,related_kwargs=None,root_id_delay=None,
                        moveTreeNode=True,excludeRoot=None,resolved=False,searchCode=None,**kwargs):
        
        treeattr = dict(storepath=storepath,hideValues=True,draggable=draggable,identifier='treeIdentifier',
                            labelAttribute='caption',selectedLabelClass='selectedTreeNode',searchCode=searchCode,dropTarget=True)
        treeattr.update(kwargs)
        if excludeRoot:
            treeattr['storepath'] = '%(storepath)s.root' %treeattr
            if excludeRoot==root_id:
                treeattr['storepath'] = '%s.%s' %(treeattr['storepath'],root_id)
        tree = pane.tree(**treeattr)
        store_kwargs.update(condition_kwargs)
        tree.htableViewStore(storepath=storepath,table=table,caption_field=caption_field,condition=condition,
                            root_id=root_id,columns=columns,
                            related_kwargs=related_kwargs,
                            dbstore=dbstore,resolved=resolved,**store_kwargs)
        if moveTreeNode:
            treeattr = tree.attributes
            treeattr['onDrop_nodeattr']="""var into_pkey = dropInfo.treeItem.attr.pkey;
                                       var into_parent_id = dropInfo.treeItem.attr.parent_id;
                                        var pkey = data.pkey;
                                        var parent_id = data.parent_id;
                                        var modifiers = dropInfo.modifiers;
                                if(!modifiers && genro.dom._lastDragInfo && genro.dom._lastDragInfo.modifiers){
                                    modifiers = genro.dom._lastDragInfo.modifiers;
                                    //fix firefox debian
                                }
                               genro.serverCall("ht_moveHierarchical",{table:'%s',pkey:pkey,
                                                                        into_pkey:into_pkey,
                                                                        parent_id:parent_id,
                                                                        into_parent_id:into_parent_id,
                                                                        modifiers:modifiers},
                                                function(result){
                                                });""" %table
            treeattr['dropTargetCb']="""return this.form? this.form.locked?false:THTree.dropTargetCb(this,dropInfo):THTree.dropTargetCb(this,dropInfo);"""  
        tree.onDbChanges(action="""
            if(excludeRoot===true){
                excludeRoot = '_forest_';
            }
            THTree.refreshTree(dbChanges,store,treeNode,excludeRoot);
        """,table=table,store='=%s' %treeattr['storepath'],treeNode=tree,excludeRoot=excludeRoot) 
        tree.dataController("""storebag._nodes.forEach(function(n){n.getValue('reload')});""",
                            storebag='=%s' %treeattr['storepath'],
                            treeNode=tree,subscribe_public_changed_partition=True)

        if root_id:
            pane.dataController("""
                var rootNode = storebag.getNode("root");
                if(rootNode){
                    if(rootNode._value){
                        rootNode.getValue('reload',{root_id:root_id});
                    }
                    tree.publish('onChangedRoot',{root_id:root_id});                    
                }
            """,root_id=root_id,storebag='=%s' %storepath,
            _delay=root_id_delay if root_id_delay is not None else 100,tree=tree)
        return tree


class TableHandlerHierarchicalView(BaseComponent):
    py_requires='th/th_picker:THPicker,th/th_tree:HTableTree'

    @struct_method
    def ht_treeViewer(self,pane,caption_field=None,_class=None,excludeRoot=None,**kwargs):
        pane.attributes['height'] = '100%'
        pane.attributes['overflow'] = 'hidden'
        box = pane.div(datapath='.#parent.hview',text_align='left',height='100%',childname='treebox')        
        formNode = pane.parentNode.attributeOwnerNode('formId')
        form = formNode.value
        form.store.handler('load',default_parent_id='=#FORM.record.parent_id')
        table = formNode.attr['table']
        hviewTree = box.hviewTree(table=table,caption_field=caption_field,_class=_class or 'noIcon',excludeRoot=excludeRoot,**kwargs)
        form.htree = hviewTree
        hviewTree.dataController("this.form.load({destPkey:selected_pkey || '*norecord*'});",selected_pkey="^.tree.pkey")
        hviewTree.dataController("""
            if(pkey==null){
                tree.widget.setSelectedPath(null,{value:'root'});
            }
            if(!pkey || pkey=='*newrecord*'){
                return;
            }
            if(pkey==currSelectedPkey){
                return;
            }
            PUT .tree.pkey = pkey;
            var selectedPath = currHierarchicalPkey? currHierarchicalPkey.replace(/\//g,'.'):null;
            if(!excludeRoot){
                selectedPath = selectedPath?'root.'+selectedPath:'root';
            }
            tree.widget.setSelectedPath(null,{value:selectedPath});                        
        """,formsubscribe_onLoaded=True,tree=hviewTree,table=table,
            currSelectedPkey='=.tree.pkey',
            currHierarchicalPkey='=#FORM.record.hierarchical_pkey',
            excludeRoot=excludeRoot)        
        form.dataController("""var currpkey = this.form.getCurrentPkey();
                            if(currpkey!='*newrecord*'){
                                treeWdg.setSelected(treeWdg._itemNodeMap[currpkey]);
                            }""",formsubscribe_onCancel=True,treeWdg=hviewTree.js_widget)    
        return hviewTree
    
    @struct_method
    def ht_hviewTree(self,box,table=None,_class=None,**kwargs): 
        pane = box.div(height='100%').div(position='absolute',top='2px',left='2px',right='2px',bottom='2px',overflow='auto')
        tree = pane.hTableTree(table=table,childname='htree',
                          onDrag="""var sn = dragInfo.sourceNode;
                                      if(sn.widget._filteringValue || sn.form.isNewRecord() || sn.form.locked ){return false;}""", 
                          selected_pkey='.tree.pkey',
                          selected_hierarchical_pkey='.tree.hierarchical_pkey',                          
                          selectedPath='.tree.path',margin='2px',_class=_class,**kwargs)
            
        return tree
    
    def th_hviewTreePicker(self,tree,search_bar=None,picker=None,table=None,**kwargs):
        picker_kwargs = dictExtract(kwargs,'picker_')
        picker_table = self.db.table(table).column(picker).relatedTable().dbtable.fullname
        paletteCode = 'picker_%s' %picker_table.replace('.','_')
        picker_kwargs['paletteCode'] = paletteCode
        search_bar.treePicker.palettePicker(table=picker_table,
                                    autoInsert=False,
                                    multiSelect=False,
                                    picker_kwargs=picker_kwargs,
                                    dockButton=dict(parentForm=False,iconClass='iconbox app'))
        tree.attributes['onDrop_%s' %paletteCode] = """THTree.onPickerDrop(this,
                                                        data,dropInfo,{type_field:'%s',
                                                        maintable:'%s',typetable:'%s'});
                                                        """ %(picker,table,picker_table)



    @public_method
    def ht_htreeCreateChildren(self,maintable=None,typetable=None,types=None,type_field=None,parent_id=None,how_many=None):
        if not types:
            return
        how_many = how_many or 1
        tblobj = self.db.table(maintable)
        typetable = self.db.table(typetable)
        caption_field = tblobj.attributes['hierarchical'].split(',')[0]
        type_caption_field = typetable.attributes['caption_field']
        wherelist = ['$parent_id=:p_id' if parent_id else '$parent_id IS NULL']
        wherelist.append("$%s LIKE :type_caption || :suffix" %caption_field)
        where = ' AND '.join(wherelist)
        for type_id in types:
            type_record = typetable.cachedRecord(pkey=type_id,virtual_columns=type_caption_field)
            type_caption = typetable.readColumns(columns=type_caption_field,pkey=type_id)
            last_child = tblobj.query(where=where ,p_id=parent_id,
                                 order_by='$%s desc' %caption_field,
                                 type_caption=type_caption,limit=1,suffix=' %%').fetch()
            offset = 0
            if last_child:
                last_child = last_child[0]
                offset = int(last_child[caption_field].replace(type_caption,'').replace(' ','') or '0')
            for i in range(how_many):
                record = tblobj.newrecord()
                kk = offset+1+i
                record.update({type_field:type_id,'parent_id':parent_id or None,caption_field:'%s %i' %(type_caption,kk)})
                for fld in tblobj.attributes.get('hierarchical').split(','):
                    if fld!=caption_field and type_record.get(fld) is not None: #exists a field with the same name in type table
                        record[fld] = '%s_%s' %(type_record[fld],kk) 
                tblobj.insert(record)
        self.db.commit()
    

    @struct_method
    def ht_slotbar_form_hbreadcrumb(self,pane,**kwargs):
        table = pane.getInheritedAttributes().get('table')
        tblobj = self.db.table(table)
        hierarchical = tblobj.attributes['hierarchical']
        hfield = hierarchical.split(',')[0]
        breadroot = pane.div()
        pane.dataController("genro.dom.setClass(breadroot.getParentNode(),'lockedToolbar',locked)",
                            locked='^#FORM.controller.locked',breadroot=breadroot)
        pane.dataController("""
                           if(this.form.isNewRecord()){
                                return;
                           }
                           var pathlist = main_h_desc?main_h_desc.split('/'):[];
                           var pkeylist = hpkey?hpkey.split('/'):[];
                           rootnode.freeze().clearValue();
                           var label,pkey;
                           var path2set = '_root_';
                           var that = this;
                           var standardCb = function(evt){
                                if(evt.target && evt.target.sourceNode){
                                    var sn = evt.target.sourceNode;
                                    if(sn.attr.pkey && sn.attr.pkey!=this.form.getCurrentPkey()){
                                        this.form.load({destPkey:sn.attr.pkey});
                                    }else if(sn.attr._addchild){
                                        if(!this.form.isNewRecord()){
                                            this.form.newrecord({parent_id:this.form.getCurrentPkey()});
                                        }
                                    }
                                }
                           }
                           var toggleTreeCb = function(){
                                this.form.sourceNode.getWidget().setRegionVisible('left','toggle');
                           }
                           var row = rootnode._('table',{'border_spacing':0,connect_onclick:standardCb})._('tbody')._('tr');
                           row._('td')._('div',{'connect_onclick':toggleTreeCb,_class:'bread_root',tip:rootName});
                           for(var i=0;i<pathlist.length;i++){
                               label = pathlist[i];
                               row._('td')._('div',{'_class':'bread_middle'});
                               row._('td',{'innerHTML':label,_class:'iconbox_text',pkey:pkeylist[i]});
                           }
                           row._('td')._('div',{'_class':'last_bread_middle bread_middle'});
                           row._('td')._('div',{'_class':'bread_add',_addchild:true});
                           rootnode.unfreeze();
                            """,rootnode=breadroot,table=table,
                                datapath='#FORM.#parent',
                               rootName = tblobj.name_plural,
                               currpath = '=.hview.tree.path',
                               hfield=hfield,
                               main_h_desc = '=.form.record.hierarchical_%s' %hfield,
                               hpkey = '=.form.record.hierarchical_pkey',
                               _fired='^.form.controller.loaded',
                               add_label='!!Add')
    @extract_kwargs(relation=True)
    @struct_method
    def ht_relatedTableHandler(self,tree,th,dropOnRoot=True,
                                inherited=None,relation_kwargs=None):
        relation_table = relation_kwargs.pop('table',None)
        vstore = th.view.store
        vstoreattr = vstore.attributes
        grid = th.view.grid
        gridattr = grid.attributes
        maintable = tree.getInheritedAttributes()['table']
        maintableobj = self.db.table(maintable)
        if inherited:
            bar = th.view.top.bar.replaceSlots('searchOn','showInherited,10,searchOn')
            bar.showInherited.checkbox(value='^.showInherited',label='!!Show Inherited',
                                    parentForm=False,label_color='#666')
        if not relation_table:
            tblalias = maintableobj.pkg.tables['%s_alias' %maintable.split('.')[1]]
            relation_table = tblalias.fullname if tblalias else ''
        dragTable = th.attributes['table']
        fkey_name = vstoreattr.get('_fkey_name')
        assert fkey_name or relation_table, 'If there is no relation: relation_table is mandatory'
        fkey_name_alt = dictExtract(vstoreattr,'_fkey_name_')
        condlist = []
        condpars = dict(suffix='/%%',curr_hpkey='=#FORM.record.hierarchical_pkey',showInherited='^.showInherited')
        hiddencolumns = gridattr['hiddencolumns'].split(',') if gridattr.get('hiddencolumns') else []
        for k in relation_kwargs.keys():
            altrelname = k.split('_')[0] #altrelname must not contain '_'
            if altrelname not in relation_kwargs:
                relation_kwargs[altrelname] = dictExtract(relation_kwargs,altrelname+'_',pop=True)
        for k,v in fkey_name_alt.items():
            condlist.append(" $%s = :fkey " %v)
            if k in relation_kwargs:
                hiddencolumns.append("$%s" %v)
                relation_kwargs[k]['fkey_name'] = v
                assert relation_kwargs[k]['modifiers'],'Missing modifiers for handling alt relation %s' %k
        
        rel_fkey_name = False 
        if fkey_name:
            hiddencolumns.append('@%s.hierarchical_pkey AS one_hpkey' %fkey_name)
            condlist.append("""( CASE WHEN :fkey IS NULL 
                                     THEN $%s IS NULL 
                                     ELSE (( :showInherited IS TRUE AND (@%s.hierarchical_pkey ILIKE (:curr_hpkey || :suffix)) ) OR ( $%s =:fkey ) ) 
                                 END ) """ %(fkey_name,fkey_name,fkey_name))                     
            vstoreattr['_if'] = None #remove the default _if
            vstoreattr['_else'] = None
        if relation_table:
            mainjoiner = maintableobj.model.getJoiner(relation_table)
            relatedjoiner = self.db.table(dragTable).model.getJoiner(relation_table)
            if relatedjoiner:
                relation_name = relatedjoiner['relation_name']
                rel_fkey_name = mainjoiner['many_relation'].split('.')[-1]
                condlist.append("""
                ( ( @%s.%s =:fkey ) OR 
                    ( :showInherited IS TRUE AND
                            ( @%s.@%s.hierarchical_pkey ILIKE (:curr_hpkey || :suffix) )
                    )
                )
                """ %(relation_name,rel_fkey_name,relation_name,rel_fkey_name))
                hiddencolumns.append('@%s.@%s.hierarchical_pkey AS many_hpkey' %(relation_name,rel_fkey_name))
        vstoreattr['condition'] = ' OR '.join(condlist)
        vstoreattr['fullReloadOnChange'] = True
        vstoreattr.update(condpars)
        dragCode = 'hrows_%s' %dragTable.replace('.','_')
        trashId = False
        if fkey_name and relation_table:
            trashId=str(id(tree))
            tree.parent.div(_class='treeTrash',id=trashId,onCreated="""
                var that = this;
                var c1 = dojo.connect(window,'dragend',function(){
                    genro.dom.removeClass(that,'treeShowTrash');
                });
            """,dropTarget=True,**{'onDrop_%s' %dragCode:"""
                genro.serverCall("ht_removeAliasRows",{aliastable:"%s",dragtable:'%s',fkeys:data.alias_pkeys});
            """ %(relation_table,dragTable)})
        gridattr.update(draggable_row=True,
                        onDrag="""  if(!dragValues.gridrow){return;}
                                    var sourceNode = dragInfo.sourceNode;
                                    var curr_hfkey = sourceNode._curr_hfkey;
                                    var alt_relations = objectUpdate({},sourceNode.attr._th_alt_relations);
                                    var rows = dragValues.gridrow.rowset;
                                    var inherited_pkeys = [];
                                    var alias_pkeys = [];
                                    var pkeys = [];

                                    dojo.forEach(rows,function(r){
                                        THTreeRelatedTableHandler.onRelatedRow(r,curr_hfkey,alt_relations);
                                        var pkey = r['_pkey'];
                                        if(r['_hieararchical_inherited']){
                                            inherited_pkeys.push(pkey);
                                        }
                                        if(r['_alias_row']){
                                            alias_pkeys.push(pkey);
                                        }
                                        var d = objectExtract(r,'_altrelation_*',true)
                                        if(objectNotEmpty(d)){
                                            for(var k in d){
                                                alt_relations[k]['pkeys'] = alt_relations[k]['pkeys'] || [];
                                                alt_relations[k]['pkeys'].push(pkey)
                                            }
                                        }
                                        pkeys.push(pkey);
                                    });
                                    if(pkeys.length==alias_pkeys.length && inherited_pkeys.length==0 && !sourceNode.form.locked ){
                                        dojo.addClass(dojo.byId(sourceNode.attr.trashId),'treeShowTrash');
                                    }
                                    dragValues['%s'] = {pkeys:pkeys,inherited_pkeys:inherited_pkeys,alias_pkeys:alias_pkeys,
                                                        alt_relations:alt_relations};""" %dragCode,
                                        rowCustomClassesCb="""function(row){
                                                        return THTreeRelatedTableHandler.onRelatedRow(row,this.sourceNode._curr_hfkey,this.sourceNode.attr._th_alt_relations);
                                                      }""",                                        
                                        hiddencolumns=','.join(hiddencolumns) if hiddencolumns else None,trashId=trashId,
                                        _th_alt_relations=relation_kwargs or False
                                        )
        tree.dataController("grid._curr_hfkey = curr_hfkey;",grid=grid,tree=tree,curr_hfkey='^#FORM.record.hierarchical_pkey',
                                _if='grid')
        treeattr = tree.attributes
        treeattr['dropTargetCb_%s' %dragCode]="""if(!data){
                                                    return true;
                                                }
                                                var droppedOnVirtualNode = dropInfo.treeItem.attr._record && dropInfo.treeItem.attr._record._virtual_node;
                                                if(droppedOnVirtualNode){
                                                    return true;
                                                }
                                                if(data['inherited_pkeys']!=null || data.alias_pkeys!=null){
                                                    return data.inherited_pkeys.length==0 && data.alias_pkeys.length==0;
                                                }
                                                return true;
                                                """  

        treeattr['onDrop_%s' %dragCode] = """  var relationValue = dropInfo.treeItem.attr.pkey || null;
                                                var relationRecord = dropInfo.treeItem.attr._record || null;
                                                var modifiers = dropInfo.modifiers;
                                                var alias_on_field = this.getRelativeData('#FORM.controller.table?alias_on_field');
                                                var droppedOnVirtualNode = dropInfo.treeItem.attr._record && dropInfo.treeItem.attr._record._virtual_node;
                                                var asAlias = (relationRecord && alias_on_field)?relationRecord[alias_on_field]:(modifiers=="Shift" || droppedOnVirtualNode)
                                                if(%s){
                                                    genro.serverCall('ht_updateRelatedRows',{table:'%s',fkey_name:'%s',pkeys:data.pkeys,
                                                                                        relationValue:relationValue,modifiers:dropInfo.modifiers,
                                                                                        asAlias:asAlias,
                                                                                        relation_table:'%s',maintable:'%s',alt_relations:data.alt_relations},null,null,'POST');
                                                }else{
                                                    return false;
                                                }
                                                
                                                """ %('relationValue' if not dropOnRoot else 'true',dragTable,fkey_name,relation_table,maintable)
        
    @public_method
    def ht_updateRelatedRows(self,table=None,maintable=None,fkey_name=None, pkeys=None,
                             relationValue=None, modifiers=None, asAlias = None,
                             relation_table=None,alt_relations=None):
        tblobj = self.db.table(table)
        alt_relations_modifiers_dict = dict([(v['modifiers'],v['fkey_name']) for k,v in alt_relations.items()])
        reltblobj = None
        if alt_relations:
            for k,v in alt_relations.items():
                alt_pkeys = v.get('pkeys')
                if alt_pkeys:
                    pkeys = filter(lambda r: r not in alt_pkeys, pkeys)
                    tblobj.batchUpdate({alt_relations[k]['fkey_name']:relationValue},_pkeys=alt_pkeys)
        if relation_table:
            reltblobj = self.db.table(relation_table)
            rel_fkey_name = self.db.table(maintable).model.getJoiner(relation_table)['many_relation'].split('.')[-1]
            rkey_name = tblobj.model.getJoiner(relation_table)['many_relation'].split('.')[-1]
        if alt_relations and alt_relations_modifiers_dict.get(modifiers):
            alt_fkey_name = alt_relations_modifiers_dict[modifiers]
            tblobj.batchUpdate({alt_fkey_name:relationValue},_pkeys=pkeys)

        elif (asAlias or not fkey_name):
            if reltblobj:
                currRelatedRecords = reltblobj.query(where='$%s=:v AND $%s IS NOT NULL' %(rel_fkey_name,rkey_name),v=relationValue).fetchAsDict(rkey_name)
                for pkey in pkeys:
                    if pkey not in currRelatedRecords:
                        reltblobj.insert({rel_fkey_name:relationValue,rkey_name:pkey})
        elif fkey_name:
            tblobj.batchUpdate({fkey_name:relationValue},_pkeys=pkeys)
            if reltblobj:
                reltblobj.deleteSelection(where='$%s=:v AND $%s IN :pkeys' %(rel_fkey_name,rkey_name),pkeys=pkeys,v=relationValue)
        self.db.commit()
        
    @public_method
    def ht_removeAliasRows(self,aliastable=None,dragtable=None,fkeys=None):
        dragtblobj = self.db.table(dragtable)
        fkey_name = dragtblobj.model.getJoiner(aliastable)['many_relation'].split('.')[-1]
        self.db.table(aliastable).deleteSelection(where='$%s IN :fkeys' %fkey_name,fkeys=fkeys)
        dragtblobj.touchRecords(_pkeys=fkeys)
        self.db.commit()


