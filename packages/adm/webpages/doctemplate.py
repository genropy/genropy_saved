#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrstring import  concat, jsquote
from gnr.core.gnrbag import Bag


# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.doctemplate'
    py_requires='public:Public,standard_tables:TableHandler,foundation/macrowidgets:RichTextEditor'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Doc template'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Doc template'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('name',name='!!Name',width='20em')
        r.fieldcell('username',name='!!Username',width='10em')
        r.fieldcell('version',name='!!Version',width='20em')
        return struct
            
    def orderBase(self):
        return 'name'
        
    def queryBase(self):
        return dict(column='name',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(regions='^mainbc.regions',**kwargs)
        bc.data('mainbc.regions.left?show',False)
        bc.dataController('SET mainbc.regions.left?show = maintable?true:false',maintable='^.maintable')
        left = bc.tabContainer(region='left',width='200px',splitter=True,datapath='table',selectedPage='^statusedit')
        self.left(left)
        top = bc.contentPane(margin='5px',region='top').toolbar()
        fb = top.formbuilder(cols=6, border_spacing='4px',disabled=disabled)
        fb.field('name',width='10em')
        fb.field('version',width='4em')
        fb.field('maintable',width='100%',colspan=2)
        fb.checkbox(value='^mainbc.regions.left?show',label='Helps')        
        tc = bc.tabContainer(region='center',selectedPage='^statusedit')
        editorPane = tc.borderContainer(title='Edit',pageName='edit')
        previewPane = tc.borderContainer(title='Preview',pageName='view')
        previewPane.div(innerHTML='==dataTemplate(tpl,data)',data='^test_record.record',
                                  tpl='=form.record.content')
        self.RichTextEditor(editorPane, value='^.content', contentPars=dict(region='center'),
                            nodeId='docEditor',editorHeight='200px',toolbar=self.rte_toolbar_standard())
    def left(self,tc):
        t1 = tc.contentPane(title='Fields' ,pageName='edit')
        t1.dataRemote('.tree.fields','relationExplorer',table='^form.record.maintable',dosort=False)
        t1.tree(storepath='.tree',persist=False,
                     inspect='shift', labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     margin='6px',
                     font_size='.9em',
                     selected_fieldpath='.selpath',
                     getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                     getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")
                                     
        t2 = tc.contentPane(title='Sample Record',pageName='view')
        fb = t2.formbuilder(cols=1, border_spacing='2px')
        fb.dbSelect(dbtable='^form.record.maintable',value='^test_id',lbl='Test')
        fb.dataRecord('test_record.record','=form.record.maintable',pkey='^test_id')
        t2.tree(storepath='test_record')

    def rpc_relationExplorer(self, table=None, prevRelation='', prevCaption='', omit='',quickquery=False, **kwargs):
        if not table:
            return Bag()
        def buildLinkResolver(node, prevRelation, prevCaption):
            nodeattr = node.getAttr()
            if not 'name_long' in nodeattr:
                raise Exception(nodeattr) # FIXME: use a specific exception class
            nodeattr['caption'] = nodeattr.pop('name_long')
            nodeattr['fullcaption'] = concat(prevCaption, self._(nodeattr['caption']), ':')
            if nodeattr.get('one_relation'):
                nodeattr['_T'] = 'JS'
                if nodeattr['mode']=='O':
                    relpkg, reltbl, relfld = nodeattr['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = nodeattr['many_relation'].split('.')
                jsresolver = "genro.rpc.remoteResolver('relationExplorer',{table:%s, prevRelation:%s, prevCaption:%s, omit:%s})"
                node.setValue(jsresolver % (jsquote("%s.%s" % (relpkg, reltbl)), jsquote(concat(prevRelation, node.label)), jsquote(nodeattr['fullcaption']),jsquote(omit)))
        result = self.db.relationExplorer(table=table, 
                                         prevRelation=prevRelation,
                                         omit=omit,
                                        **kwargs)
        result.walk(buildLinkResolver, prevRelation=prevRelation, prevCaption=prevCaption)
        return result