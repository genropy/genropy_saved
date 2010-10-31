#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

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
        bc.data('tableTree',self.db.tableTreeBag(['sys'],omit=True))
        bc.dataController('SET mainbc.regions.left?show = maintable?true:false',maintable='^.maintable')
        left = bc.tabContainer(region='left',width='280px',splitter=True,datapath='table',selectedPage='^statusedit')
        self.left(left)
        top = bc.contentPane(margin='5px',region='top').toolbar()
        fb = top.formbuilder(cols=6, border_spacing='4px',disabled=disabled)
        fb.field('name',width='10em')
        fb.field('version',width='4em')
        box = fb.div(_class='fakeTextBox floatingPopup',width='15em',lbl='Table',colspan=2)
        box.span('^.maintable')
        box.menu(storepath='tableTree',modifiers='*',_class='smallmenu',action='SET .maintable = $1.fullpath')
        fb.checkbox(value='^mainbc.regions.left?show',label='!!Show fields')        
        tc = bc.tabContainer(region='center',selectedPage='^statusedit')
        editorPane = tc.contentPane(title='Edit',pageName='edit')
        previewPane = tc.borderContainer(title='Preview',pageName='view')
        previewPane.div(innerHTML='==dataTemplate(tpl,data)',data='^test_record.record',
                        tpl='=form.record.content',margin='10px')
        self.metadataForm(tc.contentPane(title='!!Metadata',pageName='metadata',datapath='.metadata'),disabled=disabled)
        self.RichTextEditor(editorPane, value='^.content',height='100%',toolbar=self.rte_toolbar_standard())
    
    def metadataForm(self,pane,disabled=None):
        fb = pane.formbuilder(cols=2, border_spacing='4px',fld_width='15em',disabled=disabled)
        fb.textbox(value='^.subject',lbl='Subject',colspan='2',width='100%')
        fb.textbox(value='^.to_address',lbl='To Address field')
        fb.textbox(value='^.from_address',lbl='From Address field')
        
        
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
                     drag_value_cb='return item.attr.fieldpath;',
                     node_draggable=True,
                     drag_class='draggedItem',
                     
                     getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                     getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")
                                     
        t2 = tc.contentPane(title='Sample Record',pageName='view')
        fb = t2.formbuilder(cols=1, border_spacing='2px')
        fb.dbSelect(dbtable='^form.record.maintable',value='^test_id',lbl='Test')
        fb.dataRecord('test_record.record','=form.record.maintable',pkey='^test_id',
                    _if='pkey')
        t2.tree(storepath='test_record')