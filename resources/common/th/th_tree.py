# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-09.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag,BagResolver
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.web.gnrwebstruct import struct_method

class TableHandlerTreeResolver(BagResolver):
    classKwargs = {'cacheTime': 300,
                   'table':None,
                   'parent_id': None,
                   'caption_field':None,
                   '_page':None}
    classArgs = ['parent_id']

    def resolverSerialize(self):
        attr = super(TableHandlerTreeResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

    def load(self):
        page = self._page
        tblobj = page.db.table(self.table)
        pkeyfield = tblobj.pkey
        where = '$parent_id IS NULL'
        if self.parent_id:
            where='$parent_id=:p_id' #sottopratiche
        caption_field = self.caption_field or tblobj.attributes.get('caption_field')
        q = tblobj.query(where=where,p_id=self.parent_id,columns='*,$child_count,$%s' %caption_field,
                         order_by='$%s' %caption_field)
        result = Bag()
        f = q.fetch()
        for r in f:
            record = dict(r)
            caption = r[caption_field]
            pkey = record[pkeyfield]
            result.setItem(pkey,TableHandlerTreeResolver(_page=page,table=self.table,parent_id=pkey),
                            caption=caption,
                            child_count=record['child_count'],pkey=pkey or '_all_',
                            parent_id=self.parent_id,
                            treeIdentifier=pkey)
        return result

class TableHandlerHierarchicalView(BaseComponent):
    js_requires='th/th_tree'

    @public_method    
    def ht_moveHierarchical(self,table=None,pkey=None,into_pkey=None):
        into_pkey = into_pkey or None
        self.db.table(table).batchUpdate(dict(parent_id=into_pkey),where='$id=:pkey',pkey=pkey)
        self.db.commit()
        
    @struct_method
    def ht_slotbar_treeViewer(self,pane,**kwargs):
        pane.attributes['height'] = '100%'
        box = pane.div(height='100%',position='relative',datapath='.#parent.hview',text_align='left')
        formNode = pane.parentNode.attributeOwnerNode('formId')
        form = formNode.value
        form.store.handler('load',default_parent_id='=#FORM/parent/#FORM.record.parent_id')
        table = formNode.attr['table']
        hviewTree = box.hviewTree()
        hviewTree.htableViewStore(table=table)
        hviewTree.dataController("this.form.load({destPkey:selected_pkey});",selected_pkey="^.tree.pkey")
        hviewTree.dataController("""
            if(!pkey){
                return;
            }
            if(pkey==currSelectedPkey){
                return;
            }
            PUT .tree.pkey = pkey;
            var path = ['root'];
            var recordpath = genro.serverCall('ht_pathFromPkey',{pkey:this.form.getCurrentPkey(),table:table});
            if(recordpath){
                path = path.concat(recordpath.split('.'));
            }
            path = path.join('.');
            tree.widget.setSelectedPath(null,{value:path});                        
        """,formsubscribe_onLoaded=True,tree=hviewTree,table=table,currSelectedPkey='=.tree.pkey')
        form.dataController("""var currpkey = this.form.getCurrentPkey();
                            if(currpkey!='*newrecord*'){
                                treeWdg.setSelected(treeWdg._itemNodeMap[currpkey]);
                            }""",formsubscribe_onCancel=True,treeWdg=hviewTree.js_widget)        
         
    @struct_method
    def ht_htableViewStore(self,tree,table=None):
        b = Bag()
        tblobj = self.db.table(table)
        b.setItem('root',TableHandlerTreeResolver(_page=self,table=table),caption=tblobj.name_long,child_count=1,pkey='',treeIdentifier='_root_')
        treeattr = tree.attributes
        treeattr['onDrop_nodeattr']="""var into_pkey = dropInfo.treeItem.attr.pkey;
                               var pkey = data.pkey;
                               genro.serverCall("ht_moveHierarchical",{table:'%s',pkey:pkey,into_pkey:into_pkey},
                                                function(result){
                                                });""" %table
        treeattr['dropTargetCb']="""return THTree.dropTargetCb(this,dropInfo);"""  
        pane = tree.parent
        pane.data('.store',b,childname='store',caption=tblobj.name_plural,table=table)
        pane.dataController("console.log(resolver_type,selectionName)",resolver_type="^.resolver_type",selectionName='=.#parent.view.store?selectionName')
        pane.onDbChanges(action="""THTree.refreshTree(dbChanges,store,treeNode);""",table=table,store='=.store',treeNode=tree) 
        
    @extract_kwargs(tree=True)
    @struct_method
    def th_hviewTree(self,parent,storepath='.store',tree_kwargs=None,**kwargs):
        box = parent.div(position='absolute',top='2px',left='2px',right='2px',bottom='2px',overflow='auto')
        tree = box.tree(storepath=storepath,_class='fieldsTree', hideValues=True,
                            draggable=True,childname='htree',
                            onDrag="""var sn = dragInfo.sourceNode;
                                      if(sn.form.isNewRecord() || sn.form.isDisabled()){return false;}""", 
                            selectedLabelClass='selectedTreeNode',
                            labelAttribute='caption',
                            dropTarget=True,
                            selected_pkey='.tree.pkey',
                            selectedPath='.tree.path',                            
                            identifier='treeIdentifier',
                            **tree_kwargs)
        return tree
        
    @public_method
    def ht_pkeyFromPath(self,table=None,hpath=None,hfield=None):
        tblobj = self.db.table(table)
        if not hfield:
            hierarchical = tblobj.attributes['hierarchical']
            hfield = hierarchical.split(',')[0]
        return tblobj.readColumns(columns='$%s' %tblobj.pkey,where='$hierarchical_%s=:hpath' %hfield,hpath=hpath)
    
    @public_method
    def ht_pathFromPkey(self,table=None,pkey=None,hfield=None):
        tblobj = self.db.table(table)
        if not hfield:
            hierarchical = tblobj.attributes['hierarchical']
            hfield = hierarchical.split(',')[0]
        hdescription = tblobj.readColumns(columns='$hierarchical_%s' %hfield,pkey=pkey)
        where = " ( :hdescription = $hierarchical_%s ) OR ( :hdescription ILIKE $hierarchical_%s || :suffix) " %(hfield,hfield)
        f = tblobj.query(where=where,hdescription=hdescription,suffix='.%%',order_by='$hierarchical_%s' %hfield).fetch()
        if f:
            return '.'.join([r['pkey'] for r in f])
        
    def ht_hierarchicalForm(self,form,hierarchical=None):
        if hierarchical:
            form.left.attributes.update(hidden=True,splitter=True,width='200px')
            bc = form.left.borderContainer()
            pane = bc.contentPane(region='center')
            bar = pane.slotBar('treebar,treeViewer,2',width='100%')
            sc = bc.stackContainer(region='bottom',hidden=True,selectedPage='^#FORM.#parent.hview.resolver_type')
            bar.treebar.slotToolbar('stackButtons',stackButtons_height='18px',stackButtons_font_size='.9em',stackButtons_stackNode=sc,height='20px')
            sc.contentPane(title='!!All',pageName='all_records')
            sc.contentPane(title='!!In selection',pageName='selection')

            
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
                           var pathlist = main_h_desc?main_h_desc.split('.'):[];
                           rootnode.freeze().clearValue();
                           var label;
                           var path2set = '_root_';
                           var that = this;
                           var standardCb = function(evt){
                                if(evt.target && evt.target.sourceNode){
                                    var sn = evt.target.sourceNode;
                                    if(sn.attr._hpath && sn.attr._hpath!=main_h_desc){
                                        this.form.load({destPkey:genro.serverCall('ht_pkeyFromPath',{table:table,hpath:sn.attr._hpath,hfield:hfield})});
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
                               row._('td',{'innerHTML':label,_class:'iconbox_text',_hpath:pathlist.slice(0,i+1).join('.')});
                           }
                           row._('td')._('div',{'_class':'last_bread_middle bread_middle'});
                           row._('td')._('div',{'_class':'bread_add',_addchild:true});
                           rootnode.unfreeze();
                            """,rootnode=breadroot,table=table,
                                datapath='#FORM.#parent',
                               rootName = tblobj.name_plural,
                               currpath = '=.hview.tree.path',
                               hfield=hfield,
                               main_h_desc = '^.form.record.hierarchical_%s' %hfield,
                               add_label='!!Add')


class TableHandlerTree(TableHandlerHierarchicalView):
    py_requires='th/th:TableHandler'
    @extract_kwargs(condition=True,tree=True,default=True,picker=True)
    @struct_method
    def th_borderTableHandlerTree(self,pane,table=None,relation=None,formResource=None,treeResource=None,
                                nodeId=None,datapath=None,condition=None,
                                condition_kwargs=None,default_kwargs=None,picker_kwargs=None,**kwargs):
        if relation:
            table,condition = self._th_relationExpand(pane,relation=relation,condition=condition,
                                                    condition_kwargs=condition_kwargs,
                                                    default_kwargs=default_kwargs,original_kwargs=kwargs)
        tableCode = table.replace('.','_')
        th_root = self._th_mangler(pane,table,nodeId=nodeId)
        treeCode='T_%s' %th_root
        formCode='F_%s' %th_root
        frame = pane.framePane(datapath=datapath or '.%s'%tableCode,
                        thtree_root=treeCode,
                        thform_root=formCode,
                        nodeId=th_root,
                        table=table,
                        **kwargs)
        #frame.top.slotToolbar('2,vtitle,currentSelected,add_child,*,delrow,addrow,locker')
        bc = frame.center.borderContainer()
        default_kwargs.setdefault('parent_id','=#FORM/parent/#FORM.record.parent_id')
        form = frame.tableEditor(frameCode=formCode,formRoot=bc,formResource=formResource,
                       table=table,loadEvent='onclick',form_locked=True,
                        default_kwargs=default_kwargs,navigation=False)
        form.attributes.update(region='center',margin='2px',margin_left='4px',rounded=4,border='1px solid silver')
        form.top.bar.replaceSlots('#','hbreadcrumb,#')
        form.left.slotBar('treeViewer',splitter=True,width='300px')

