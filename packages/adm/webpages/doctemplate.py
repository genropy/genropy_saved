#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrbaghtml import BagToHtml
from gnr.core.gnrstring import templateReplace

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.doctemplate'
    css_requires='doctemplate'
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
        r.fieldcell('maintable',name='!!Name',width='20em')
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
        self.left(bc.contentPane(region='left',width='280px',splitter=True,datapath='table'))
        top = bc.contentPane(margin='5px',region='top').toolbar()
        fb = top.formbuilder(cols=6, border_spacing='4px',disabled=disabled)
        box = fb.div(_class='fakeTextBox floatingPopup',width='15em',lbl='Table',colspan=2)
        box.span('^.maintable')
        box.menu(storepath='tableTree',modifiers='*',_class='smallmenu',action='SET .maintable = $1.fullpath')
        fb.field('name',width='20em')
        fb.field('version',width='4em')
        fb.checkbox(value='^mainbc.regions.left?show',label='!!Show fields')        
        tc = bc.tabContainer(region='center')
        editorPane = tc.contentPane(title='Edit',pageName='edit',id='editpage')
        self.previewPane(tc.borderContainer(title='Preview',pageName='view',_class='preview'))
        
        
        self.metadataForm(tc.contentPane(title='!!Metadata',pageName='metadata',datapath='.metadata'),disabled=disabled)
        self.RichTextEditor(editorPane, value='^.content',height='100%',
                            toolbar=self.rte_toolbar_standard(),
                            config_contentsCss=self.getResourceUri('doctemplate.css',add_mtime=True))
                            
        bc.dataController("""
                                var virtual_columns = [];
                                dojo.query('[itemtag="virtual_column"]').forEach(function(n){
                                                var field = n.getAttribute('fieldpath');
                                                if(field){
                                                    virtual_columns.push(field);
                                                }
                                             });
                                SET .virtual_columns = virtual_columns.join(',');
                                """,_fired="^.content",_userChanges=True)
        bc.dataRpc('dummy','includeVirtualColumn',
                    virtual_column='^.virtual_columns',
                    table='=.maintable',_if='virtual_column')
    
    def previewPane(self,bc):
        top = bc.contentPane(region='top').toolbar()
        fb = top.formbuilder(cols=2, border_spacing='2px')
        fb.dbSelect(dbtable='^form.record.maintable',value='^test_id',lbl='!!Record',width='20em')
        fb.dbSelect(dbtable='adm.htmltemplate',value='^html_template_id',selected_name='html_template_name',lbl_width='10em',lbl='!!Template',width='20em',hasDownArrow=True)
        fb.dataRpc('preview','renderTemplate',table='=form.record.maintable',record_id='^test_id',
                    doctemplate='^form.record.content',htmltemplate_name='^html_template_name',_if='table&&doctemplate')
        bc.contentPane(region='center',padding='10px').div(height='100%',background='white').div(innerHTML='^preview')
        
    def rpc_includeVirtualColumn(self,table=None,virtual_column=None):
        print 'aaaa'
        with self.pageStore() as store:
            store.setItem('virtual_columns',None)
        self.includeVirtualColumn(table=table,virtual_column=virtual_column)
        
                            
    def metadataForm(self,pane,disabled=None):
        fb = pane.formbuilder(cols=2, border_spacing='4px',fld_width='15em',disabled=disabled)
        fb.textbox(value='^.subject',lbl='Subject',colspan='2',width='100%')
        fb.textbox(value='^.to_address',lbl='To Address field')
        fb.textbox(value='^.from_address',lbl='From Address field')
        
    def html_item_res(self):
        return """<span class="tplfieldpath" fieldpath="'+item.attr.fieldpath+'" itemtag = "'+item.attr.tag+'">$'+item.attr.fieldpath+'</span><span class="tplfieldcaption">'+item.attr.caption+'</span><span>&nbsp</span>"""
        
    def left(self,pane):
        pane.dataRemote('.tree.fields','relationExplorer',table='^form.record.maintable',dosort=False,caption='Fields')
        pane.tree(storepath='.tree',persist=False,
                     #inspect='shift', 
                     labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     margin='6px',
                     font_size='.9em',
                     node_draggable="""return item.attr.dtype && item.attr.dtype!='RM' && item.attr.dtype!='RO'""",
                     selected_fieldpath='.selpath',
                     drag_value_cb="""
                                      console.log(item.attr);
                                      var result = {'text/html':'%s',
                                                    'text/plain':item.attr.fieldpath};
                                      return result;""" %self.html_item_res(),
                     drag_class='draggedItem',
                     
                     getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                     getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")

    def rpc_renderTemplate(self,table=None,record_id=None,doctemplate=None,htmltemplate_name=None):
        record = self.app.rpc_getRecord(table=table,pkey=record_id)[0]
        if not record_id:
            return ''
        htmlContent = templateReplace(doctemplate,record,True)
        htmlbuilder = BagToHtml(templates=htmltemplate_name,templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        html = htmlbuilder(htmlContent=htmlContent)
        return html
        
        