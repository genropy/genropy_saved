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

class TableHandlerTree(BaseComponent):
    py_requires='th/th:TableHandler'
    js_requires='th/th_tree'

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
        bc.tableHierarchicalViewer(frameCode=treeCode,table=table)
        default_kwargs.setdefault('parent_id','=#FORM/parent/#FORM.record.parent_id')
        bc.tableEditor(frameCode=formCode,formRoot=bc,formResource=formResource,
                       table=table,loadEvent='onclick',form_locked=True,
                        default_kwargs=default_kwargs,navigation=False)
        form = bc.form
        form.attributes.update(region='center',margin='2px',margin_left='4px',rounded=4,border='1px solid silver')
        form.top.bar.replaceSlots('#','hbreadcrumb,#')
        
    @struct_method
    def th_tableHierarchicalViewer(self,parent,frameCode=None,table=None,treeResource=None,condition=None,condition_kwargs=None,**kwargs):
        frame = parent.framePane(frameCode=frameCode,margin='2px',margin_right='4px',border='1px solid silver',
                                childname='view',datapath='.view',region='left',splitter=True,
                                rounded=4,width='300px')
        b = Bag()
        tblobj = self.db.table(table)
        bar = frame.top.slotToolbar('2,vtitle,*',height='20px')
        bar.vtitle.div(tblobj.name_plural)
        
        b.setItem('root',TableHandlerTreeResolver(_page=self,table=table),caption=tblobj.name_long,child_count=1,pkey='',treeIdentifier='_root_')
        frame.data('.store',b,childname='store',caption=tblobj.name_plural) 
        tree = frame.treePane(storepath='.store',table=table)
        frame.onDbChanges(action="""THTree.refreshTree(dbChanges,store,treeNode);""",table=table,store='=.store',treeNode=tree)        
        return frame
        
    @extract_kwargs(tree=True)
    @struct_method
    def th_treePane(self,frame,storepath=None,table=None,tree_kwargs=None,**kwargs):
        box = frame.div(position='absolute',top='2px',left='2px',right='2px',bottom='2px',overflow='auto')
        tree = box.tree(storepath=storepath,_class='fieldsTree', hideValues=True,
                            draggable=True,childname='htree',
                            selectedLabelClass='selectedTreeNode',autoCollapse=True,
                            labelAttribute='caption',
                            dropTarget=True,
                            selected_pkey='.tree.pkey',
                            selectedPath='.tree.path',                            
                            identifier='treeIdentifier',
                            pkey='htree',
                            onDrop_nodeattr="""
                               var into_pkey = dropInfo.treeItem.attr.pkey;
                               var pkey = data.pkey;
                               genro.serverCall("th_moveHierarchical",{table:'%s',pkey:pkey,into_pkey:into_pkey},
                                                function(result){
                                                });""" %table,
                            dropTargetCb="""return THTree.dropTargetCb(this,dropInfo);""",
                            **tree_kwargs)
        frame.htree = tree
        return tree
        
    @public_method    
    def th_moveHierarchical(self,table=None,pkey=None,into_pkey=None):
        self.db.table(table).batchUpdate(dict(parent_id=into_pkey),where='$id=:pkey',pkey=pkey)
        self.db.commit()
        
    
    @struct_method
    def th_slotbar_hbreadcrumb(self,pane,**kwargs):
        table = pane.getInheritedAttributes().get('table')
        tblobj = self.db.table(table)
        hierarchical = tblobj.attributes['hierarchical']
        main_h = hierarchical.split(',')[0]
        breadroot = pane.div()
        pane.dataController("genro.dom.setClass(breadroot.getParentNode(),'lockedToolbar',locked)",
                            locked='^#FORM.controller.locked',breadroot=breadroot)
        pane.dataController("""
                           if(this.form.isNewRecord()){
                                return;
                           }
                           var pathlist = main_h_desc?main_h_desc.split('.'):[];
                           var pkeylist = currpath.split('.').slice(1);
                           var storeattr = store.getParentNode().attr;
                           var rootName = storeattr.caption;
                           rootnode.freeze().clearValue();
                           var label;
                           var path2set = '_root_';
                           var that = this;
                           var standardCb = function(evt){
                                if(evt.target && evt.target.sourceNode){
                                    var sn = evt.target.sourceNode;
                                    if(sn.attr._pkey!='*newrecord*'){
                                        that.setRelativeData('.view.tree.pkey',sn.attr._pkey);
                                    }else if(sn.attr._pkey=='*newrecord*'){
                                        if(!this.form.isNewRecord()){
                                            this.form.newrecord({parent_id:this.form.getCurrentPkey()});
                                        }
                                    }
                                }
                           }
                           var row = rootnode._('table',{'border_spacing':0,connect_onclick:standardCb})._('tbody')._('tr');
                           row._('td')._('div',{'connect_onclick':function(){that.setRelativeData('.view.tree.pkey','*norecord*');},
                                                _class:'bread_root',tip:rootName});
                           for(var i=0;i<pathlist.length;i++){
                               label = pathlist[i];
                               row._('td')._('div',{'_class':'bread_middle'});
                               row._('td',{'innerHTML':label,_class:'iconbox_text',_pkey:pkeylist[i]});
                           }
                           row._('td')._('div',{'_class':'last_bread_middle bread_middle'});
                           row._('td')._('div',{'_class':'bread_add',_pkey:'*newrecord*'});
                           rootnode.unfreeze();
                            """,rootnode=breadroot,
                                datapath='#FORM.#parent',
                               store = '=.view.store',
                               currpath = '=.view.tree.path',
                               main_h_desc = '^.form.record.hierarchical_%s' %main_h,
                               add_label='!!Add')


   #def xxx(self,pane):
   #    if anni_riferimento is None:
   #        anni_riferimento = '=anni_riferimento'
   #        anno= self.workdate.year
   #        anni = []
   #        for a in range(12):
   #            anni.append(str(anno))
   #            anno-=1
   #        pane.data('anni_riferimento',','.join(anni))
   #    self.subscribeTable('studio.pr_pratica',True)
   #    pane.onDbChanges(action="""PraticheTree.refreshPraticaTree(dbChanges,store,treeNode);""",table='studio.pr_pratica',store='=.tree',treeNode=tree)        
   #    b = Bag()
   #    treeIdentifier = 'R'
   #    b.setItem('root',PraticheTreeResolver(_page=self,anni=anni_riferimento,condomini=condomini,
   #                                                pratiche_studio=pratiche_studio,parentIdentifier=treeIdentifier),
   #            caption='Tutte le pratiche',caption_titolo='Tutte le pratiche',child_count=1,treeIdentifier=treeIdentifier)
   #    pane.data('.tree',b) 
   #    pane.dataRpc('dummy',self.praticheCondominioCorrente,
   #                condominio_id=condominio_id,anni=anni_riferimento,
   #                _onResult="""var treedata = GET .tree;
   #                             result.getValue();
   #                             treedata.setItem('root.condominio_corrente',result._value,result.attr);
   #                            """,_if='condominio_id',_else='var treedata = GET .tree; treedata.popNode("root.condominio_corrente");')
   #    
   #