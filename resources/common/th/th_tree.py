# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-09.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method

class TableHandlerTreeResolver(BagResolver):
    classKwargs = {'cacheTime': 300,
                   'table':None,
                   'parent_id': None,
                   'root_id':None,
                   'caption_field':None,
                   'condition':None,
                   'condition_kwargs':None,
                   '_condition_id':None,
                   'dbstore':None,
                   '_page':None}
    classArgs = ['parent_id']

    def resolverSerialize(self):
        attr = super(TableHandlerTreeResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

    def getConditionPkeys(self):
        if self._condition_id:
            condition_pkeys = self._page.pageStore().getItem('hresolver.%s' %self._condition_id)
        else:
            self._condition_id = self._page.getUuid()
            db = self._page.db
            tblobj = db.table(self.table)
            condition_kwargs = self.condition_kwargs or dict()
            valid = tblobj.query(where='$child_count=0 AND ( %s ) AND $parent_id IS NOT NULL' %self.condition,columns='$hierarchical_pkey',
                                 _storename=self.dbstore,addPkeyColumn=False,**condition_kwargs).fetch()
            condition_pkeys = set()
            for r in valid:
                for pk in r['hierarchical_pkey'].split('/'):
                    condition_pkeys.add(pk)
            condition_pkeys = list(condition_pkeys)
            with self._page.pageStore() as store:
                store.setItem('hresolver.%s' %self._condition_id,condition_pkeys)
        return condition_pkeys


    def load(self):
        page = self._page
        tblobj = page.db.table(self.table)
        pkeyfield = tblobj.pkey
        where = '$parent_id IS NULL'
        if self.root_id:
            where = '$id=:r_id'
        elif self.parent_id:
            where='$parent_id=:p_id' #sottopratiche
        caption_field = self.caption_field
        if not caption_field:
            if tblobj.attributes['hierarchical'] != 'pkey':
                caption_field = tblobj.attributes['hierarchical'].split(',')[0]
            else:
                caption_field = tblobj.attributes.get('caption_field')
            self.caption_field = caption_field

        condition_kwargs = self.condition_kwargs or dict()
        condition_pkeys = None
        if self.condition:
            condition_pkeys = self.getConditionPkeys()
            # ($parent_id=:p_id) AND (($zzz=:condizione_zzz AND ($child_count=0)) OR ( $id IN :condition_pkeys ) ) 
            where = ' ( %s ) AND ( $id IN :condition_pkeys ) ' %where
        q = tblobj.query(where=where,p_id=self.parent_id,r_id=self.root_id,columns='*,$child_count,$%s' %caption_field,
                         condition_pkeys=condition_pkeys,
                         order_by='$%s' %caption_field,_storename=self.dbstore,**condition_kwargs)
        result = Bag()
        f = q.fetch()
        for r in f:
            record = dict(r)
            caption = r[caption_field]
            pkey = record[pkeyfield]
            child_count=record['child_count']
            value = TableHandlerTreeResolver(_page=page,table=self.table,parent_id=pkey,caption_field=self.caption_field,dbstore=self.dbstore,condition=self.condition,_condition_id=self._condition_id) if child_count else None
            result.setItem(pkey,value,
                            caption=caption,
                            child_count=child_count,pkey=pkey or '_all_',
                            parent_id=self.parent_id,
                            hierarchical_pkey=record['hierarchical_pkey'],
                            treeIdentifier=pkey,_record=record)
        return result


class HTableTree(BaseComponent):
    js_requires='th/th_tree'

    @struct_method
    def ht_hdbselect(self,pane,caption_field=None,**kwargs):
        dbselect = pane.dbselect(**kwargs)
        attr = dbselect.attributes
        menupath = 'gnr.htablestores.%(dbtable)s' %attr
        attr['hasDownArrow'] = True
        dbselect_condition = attr.get('condition')
        dbselect_condition_kwargs = dictExtract(attr,'condition_')
        attr['condition'] = '$child_count=0' if not dbselect_condition else ' ( %s ) AND $child_count=0' %dbselect_condition
        pane.dataRemote(menupath,self.ht_remoteHtableViewStore,table=attr['dbtable'],
                        condition=dbselect_condition,
                        condition_kwargs=dbselect_condition_kwargs,
                        cacheTime=0,caption_field=caption_field)
        dbselect.menu(storepath='%s.root' %menupath,_class='smallmenu',modifiers='*',selected_pkey=attr['value'].replace('^',''))
        
        
    #@struct_method
    #def ht_htableViewStore(self,pane,table=None,storepath='.store',caption_field=None,condition=None,caption=None,dbstore=None,root_id=None,**kwargs):
    #    b = Bag()
    #    tblobj = self.db.table(table)
    #    caption = caption or tblobj.name_plural
    #    if condition:
    #        pane.dataRpc(storepath,self.ht_remoteHtableViewStore,
    #                    table=table,
    #                    caption_field=caption_field,
    #                    condition=condition,
    #                    childname='store',caption=caption,dbstore=dbstore,
    #                    **kwargs)
    #    else:
    #        b.setItem('root',TableHandlerTreeResolver(_page=self,table=table,caption_field=caption_field,dbstore=dbstore,parent_id=root_id),caption=tblobj.name_long,
    #                                                child_count=1,pkey='',treeIdentifier='_root_')
    #        pane.data(storepath,b,childname='store',caption=caption,table=table) 
#

    @struct_method
    def ht_htableViewStore(self,pane,table=None,storepath='.store',caption_field=None,condition=None,caption=None,dbstore=None,root_id=None,**kwargs):
        b = Bag()
        tblobj = self.db.table(table)
        caption = caption or tblobj.name_plural
        if condition:
            pane.dataRpc(storepath,self.ht_remoteHtableViewStore,
                        table=table,
                        caption_field=caption_field,
                        condition=condition,
                        childname='store',caption=caption,dbstore=dbstore,
                        **kwargs)
        else:
            b.setItem('root',TableHandlerTreeResolver(_page=self,table=table,caption_field=caption_field,dbstore=dbstore,root_id=root_id),caption=tblobj.name_long,
                                                    child_count=1,pkey='',treeIdentifier='_root_')
            pane.data(storepath,b,childname='store',caption=caption,table=table) 
            if root_id:
                pane.dataController("""
                    var rootNode = storebag.getNode("root");
                    if(rootNode && rootNode._value){
                        rootNode.getValue('reload',{root_id:root_id});
                    }
                    """,root_id=root_id,storebag='=%s' %storepath,_delay=1)

    @public_method
    def ht_remoteHtableViewStore(self,table=None,caption_field=None,condition=None,
                                    condition_kwargs=None,caption=None,dbstore=None,**kwargs):
        b = Bag()
        tblobj = self.db.table(table)
        caption = caption or tblobj.name_plural
        condition_kwargs = condition_kwargs or dict()
        condition_kwargs.update(dictExtract(kwargs,'condition_'))
        b.setItem('root',TableHandlerTreeResolver(_page=self,table=table,caption_field=caption_field,condition=condition,dbstore=dbstore,
                                                condition_kwargs=condition_kwargs),caption=caption,child_count=1,pkey='',treeIdentifier='_root_')
        return b

    @public_method    
    def ht_moveHierarchical(self,table=None,pkey=None,into_pkey=None):
        into_pkey = into_pkey or None
        self.db.table(table).batchUpdate(dict(parent_id=into_pkey),where='$id=:pkey',pkey=pkey)
        self.db.commit()

    @public_method
    def ht_pathFromPkey(self,table=None,pkey=None,hfield=None):
        tblobj = self.db.table(table)
        if not hfield:
            hierarchical = tblobj.attributes['hierarchical']
            hfield = hierarchical.split(',')[0]
        hdescription = tblobj.readColumns(columns='$hierarchical_%s' %hfield,pkey=pkey)
        where = " ( :hdescription = $hierarchical_%s ) OR ( :hdescription ILIKE $hierarchical_%s || :suffix) " %(hfield,hfield)
        f = tblobj.query(where=where,hdescription=hdescription,suffix='/%%',order_by='$hierarchical_%s' %hfield).fetch()
        if f:
            return '.'.join([r['pkey'] for r in f])
        
    
    @extract_kwargs(condition=dict(slice_prefix=False))
    @struct_method
    def ht_hTableTree(self,pane,storepath='.store',table=None,root_id=None,draggable=True,
                        caption_field=None,condition=None,caption=None,dbstore=None,condition_kwargs=None,**kwargs):
        
        treeattr = dict(storepath=storepath,hideValues=True,draggable=draggable,identifier='treeIdentifier',
                            labelAttribute='caption',dropTarget=True,selectedLabelClass='selectedTreeNode',_class='fieldsTree')
        treeattr.update(kwargs)
        tree = pane.tree(**treeattr)
        tree.htableViewStore(storepath=treeattr['storepath'],table=table,caption_field=caption_field,condition=condition,root_id=root_id,**condition_kwargs)
        treeattr = tree.attributes
        treeattr['onDrop_nodeattr']="""var into_pkey = dropInfo.treeItem.attr.pkey;
                               var pkey = data.pkey;
                               genro.serverCall("ht_moveHierarchical",{table:'%s',pkey:pkey,into_pkey:into_pkey},
                                                function(result){
                                                });""" %table
        treeattr['dropTargetCb']="""return this.form? this.form.locked?false:THTree.dropTargetCb(this,dropInfo):THTree.dropTargetCb(this,dropInfo);"""  
        tree.onDbChanges(action="""THTree.refreshTree(dbChanges,store,treeNode);""",table=table,store='=%s' %treeattr['storepath'],treeNode=tree) 
        return tree


class TableHandlerHierarchicalView(BaseComponent):
    py_requires='th/th_picker:THPicker,th/th_tree:HTableTree'

    @struct_method
    def ht_treeViewer(self,pane,caption_field=None,**kwargs):
        pane.attributes['height'] = '100%'
        pane.attributes['overflow'] = 'hidden'
        box = pane.div(position='relative',datapath='.#parent.hview',text_align='left',height='100%',childname='treebox')        
        formNode = pane.parentNode.attributeOwnerNode('formId')
        form = formNode.value
        form.store.handler('load',default_parent_id='=#FORM/parent/#FORM.record.parent_id')
        table = formNode.attr['table']
        
        hviewTree = box.hviewTree(table=table,caption_field=caption_field,**kwargs)
        form.htree = hviewTree
        hviewTree.dataController("this.form.load({destPkey:selected_pkey});",selected_pkey="^.tree.pkey")
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
            var selectedPath = currHierarchicalPkey?'root.'+currHierarchicalPkey.replace(/\//g,'.'):'root';
            tree.widget.setSelectedPath(null,{value:selectedPath});                        
        """,formsubscribe_onLoaded=True,tree=hviewTree,table=table,currSelectedPkey='=.tree.pkey',currHierarchicalPkey='=#FORM.record.hierarchical_pkey')        
        form.dataController("""var currpkey = this.form.getCurrentPkey();
                            if(currpkey!='*newrecord*'){
                                treeWdg.setSelected(treeWdg._itemNodeMap[currpkey]);
                            }""",formsubscribe_onCancel=True,treeWdg=hviewTree.js_widget)    
        return hviewTree
    
    @struct_method
    def ht_hviewTree(self,box,table=None,picker=None,**kwargs):  
        if picker: 
            bar = box.slotToolbar('*,treePicker,2',height='20px')
        pane = box.div(position='relative',height='100%',padding='2px')
        tree = pane.hTableTree(table=table,childname='htree',
                          onDrag="""var sn = dragInfo.sourceNode;
                                      if(sn.form.isNewRecord() || sn.form.locked ){return false;}""", 
                          selected_pkey='.tree.pkey',
                          selected_hierarchical_pkey='.tree.hierarchical_pkey',                          
                          selectedPath='.tree.path',margin='2px')
        if picker:
            picker_kwargs = dictExtract(kwargs,'picker_')
            picker_table = self.db.table(table).column(picker).relatedTable().dbtable.fullname
            paletteCode = 'picker_%s' %picker_table.replace('.','_')
            picker_kwargs['paletteCode'] = paletteCode
            bar.treePicker.palettePicker(table=picker_table,autoInsert=False,multiSelect=False,**picker_kwargs)
            tree.attributes['onDrop_%s' %paletteCode] = "THTree.onPickerDrop(this,data,dropInfo,{type_field:'%s',maintable:'%s',typetable:'%s'});" %(picker,table,picker_table)

        return tree

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
            type_caption = typetable.readColumns(columns=type_caption_field,pkey=type_id)
            last_child = tblobj.query(where=where ,p_id=parent_id,
                                 order_by='$%s desc' %caption_field,
                                 type_caption=type_caption,limit=1,suffix=' %%').fetch()
            offset = 0
            if last_child:
                last_child = last_child[0]
                offset = int(last_child[caption_field].replace(type_caption,'').replace(' ','') or '0')
            for i in range(how_many):
                record = {type_field:type_id,'parent_id':parent_id or None,caption_field:'%s %i' %(type_caption,offset+1+i)}
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
    @struct_method
    def ht_relatedTableHandler(self,tree,th,relation_table=None):
        vstore = th.view.store
        vstoreattr = vstore.attributes
        grid = th.view.grid
        gridattr = grid.attributes
        maintable = tree.getInheritedAttributes()['table']
        maintableobj = self.db.table(maintable)
        bar = th.view.top.bar.replaceSlots('searchOn','showInherited,10,searchOn')
        bar.showInherited.checkbox(value='^.showInherited',label='!!Show Inherited',parentForm=False,label_color='#666')
        if not relation_table:
            tblalias = maintableobj.pkg.tables['%s_alias' %maintable.split('.')[1]]
            relation_table = tblalias.fullname if tblalias else ''
                    
        dragTable = th.attributes['table']
        fkey_name = vstoreattr.get('_fkey_name')
        assert fkey_name or relation_table, 'If there is no relation: relation_table is mandatory'
        condlist = []
        condpars = dict(suffix='/%%',curr_fkey='=#FORM.pkey',curr_hpkey='=#FORM.record.hierarchical_pkey',showInherited='^.showInherited')
        
        hiddencolumns = gridattr.get('hiddencolumns') or []
        rel_fkey_name = False 
        if fkey_name:
            hiddencolumns.append('@%s.hierarchical_pkey AS one_hpkey' %fkey_name)
            condlist.append("""( CASE WHEN :curr_fkey IS NULL 
                                     THEN $%s IS NULL 
                                     ELSE (( :showInherited AND (@%s.hierarchical_pkey ILIKE (:curr_hpkey || :suffix)) ) OR ( $%s =:curr_fkey ) ) 
                                 END )""" %(fkey_name,fkey_name,fkey_name)) 
            vstoreattr['_if'] = None #remove the default _if
            vstoreattr['_else'] = None
        if relation_table:
            mainjoiner = maintableobj.model.getJoiner(relation_table)
            relatedjoiner = self.db.table(dragTable).model.getJoiner(relation_table)

            relation_name = relatedjoiner['relation_name']
            
            rel_fkey_name = mainjoiner['many_relation'].split('.')[-1]
            condlist.append("""
            ( ( @%s.%s =:curr_fkey ) OR 
                  ( :showInherited AND
                        ( @%s.@%s.hierarchical_pkey ILIKE (:curr_hpkey || :suffix) )
                  )
            )
            """ %(relation_name,rel_fkey_name,relation_name,rel_fkey_name))
            hiddencolumns.append('@%s.@%s.hierarchical_pkey AS many_hpkey' %(relation_name,rel_fkey_name))
        
        vstoreattr['condition'] = ' OR '.join(condlist)

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

        gridattr.update(onDrag="""  if(!dragValues.gridrow){return;}
                                    var sourceNode = dragInfo.sourceNode;
                                    var curr_hfkey = sourceNode._curr_hfkey;
                                    var rows = dragValues.gridrow.rowset;
                                    var inherited_pkeys = [];
                                    var alias_pkeys = [];
                                    var pkeys = [];
                                    dojo.forEach(rows,function(r){
                                        THTreeRelatedTableHandler.onRelatedRow(r,curr_hfkey);
                                        var pkey = r['_pkey'];
                                        if(r['_hieararchical_inherited']){
                                            inherited_pkeys.push(pkey);
                                        }
                                        if(r['_alias_row']){
                                            alias_pkeys.push(pkey);
                                        }
                                        pkeys.push(pkey);
                                    });
                                    if(pkeys.length==alias_pkeys.length && inherited_pkeys.length==0 && !sourceNode.form.locked ){
                                        dojo.addClass(dojo.byId(sourceNode.attr.trashId),'treeShowTrash');
                                    }
                                    dragValues['%s'] = {pkeys:pkeys,inherited_pkeys:inherited_pkeys,alias_pkeys:alias_pkeys};""" %dragCode,
                                        rowCustomClassesCb="""function(row){
                                                        return THTreeRelatedTableHandler.onRelatedRow(row,this.sourceNode._curr_hfkey);
                                                      }""",                                        
                                        hiddencolumns=','.join(hiddencolumns) if hiddencolumns else None,trashId=trashId)
        tree.dataController("grid._curr_hfkey = curr_hfkey;",grid=grid,tree=tree,curr_hfkey='^#FORM.record.hierarchical_pkey')
        treeattr = tree.attributes
        treeattr['dropTargetCb_%s' %dragCode]="""if(data['inherited_pkeys']!=null || data.alias_pkeys!=null){
                                                    return data.inherited_pkeys.length==0 && data.alias_pkeys.length==0;
                                                }return true;
                                                """  

        treeattr['onDrop_%s' %dragCode] = """  var relationValue = dropInfo.treeItem.attr.pkey;
                                                genro.serverCall('ht_updateRelatedRows',{table:'%s',fkey_name:'%s',pkeys:data.pkeys,
                                                                                        relationValue:relationValue,modifiers:dropInfo.modifiers,
                                                                                        relation_table:'%s',maintable:'%s'},null,null,'POST');
                                                """ %(dragTable,fkey_name,relation_table,maintable)
        
    @public_method
    def ht_updateRelatedRows(self,table=None,maintable=None,fkey_name=None, pkeys=None,
                             relationValue=None,modifiers=None,relation_table=None):
        tblobj = self.db.table(table)
        reltblobj = None
        if relation_table:
            reltblobj = self.db.table(relation_table)
            rel_fkey_name = self.db.table(maintable).model.getJoiner(relation_table)['many_relation'].split('.')[-1]
            rkey_name = tblobj.model.getJoiner(relation_table)['many_relation'].split('.')[-1]
        if modifiers == 'Shift' or not fkey_name:
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




   #@public_method
   #def ht_remoteTreeData(self, *args,**kwargs):
   #    if 'storename' in kwargs:
   #        self.db.use_store(kwargs['storename'])
   #    return self.ht_treeDataStore(*args,**kwargs)
   #
