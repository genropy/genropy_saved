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
            result.setItem(pkey,TableHandlerTreeResolver(_page=page,parent_id=pkey),
                            caption=caption,
                            child_count=record['child_count'],pkey=pkey,
                            parent_id=self.parent_id,
                            treeIdentifier=pkey)
        return result

class TableHandlerTree(BaseComponent):
    @struct_method
    def th_tableHierarchicalViewer(self,pane,table=None):
        b = Bag()
        tblobj = self.db.table(table)
        b.setItem('root',TableHandlerTreeResolver(_page=self,table=table),caption=tblobj.name_long,child_count=1)
        pane.data('.store',b) 
        
        pane.treePane(storepath='.store')

    @extract_kwargs(tree=True,store=True)
    @struct_method
    def th_treePane(self,pane,storepath=None,
                        tree_kwargs=None,**kwargs):
        box = pane.div(position='absolute',top='2px',left='2px',right='2px',bottom='2px',overflow='auto')
        tree = box.tree(storepath=storepath,_class='fieldsTree', hideValues=True,
                            font_size='.9em',
                            margin='6px',draggable=True,
                            selectedLabelClass='selectedTreeNode',autoCollapse=True,
                            labelAttribute='caption',
                            dropTarget=True,
                           #dragTags='pratiche_tree',
                           #dropTags='pratiche_tree,eventi_row',
                           #identifier='treeIdentifier',
                           #onDrop_gridrow="""
                           #    var pkeys = [];
                           #    var rowset = data.rowset;
                           #    dojo.forEach(rowset,function(r){pkeys.push(r['_pkey'])});
                           #    var kwargs = {'pkeys':pkeys,pratica_id:dropInfo.treeItem.attr.pkey};
                           #    kwargs.alias = dropInfo.event.shiftKey;
                           #    if(kwargs.pratica_id && kwargs.pkeys && kwargs.pkeys.length>0){
                           #        genro.serverCall('_table.studio.pr_evento.assegnaInPratica',kwargs,function(){});
                           #    }
                           #""",
                           #onDrop_nodeattr="""var into_pkey = dropInfo.treeItem.attr.pkey;
                           #   var pkey = data.pkey;
                           #   var condominio_id= dropInfo.treeItem.attr.condominio_id;
                           #   genro.serverCall("_table.studio.pr_pratica.riordino_pratiche",{pkey:pkey,into_pkey:into_pkey,condominio_id:condominio_id},
                           #                    function(result){
                           #                    });""",
                           #dropTargetCb="""return PraticheTree.dropTargetCb(this,dropInfo);""",
                            **tree_kwargs)
        return tree
        
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