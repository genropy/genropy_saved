#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag


# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    pageOptions={'openMenu':False}

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
        bc.data('tableTree',self.db.tableTreeBag(['sys'],omit=True,tabletype='main'))
        bc.dataController('SET mainbc.regions.left?show = maintable?true:false',maintable='^.maintable')
        self.left(bc.contentPane(region='left',width='280px',splitter=True,datapath='table'))
        top = bc.contentPane(margin='5px',region='top').toolbar()
        fb = top.formbuilder(cols=6, border_spacing='4px',disabled=disabled)
        
        box = fb.field('maintable',width='15em',readOnly=True,validate_notnull=True) #fb.div(_class='fakeTextBox floatingPopup',width='15em',lbl='Table',colspan=2)
        box.menu(storepath='tableTree',modifiers='*',_class='smallmenu',action='SET .maintable = $1.fullpath')
        fb.field('name',width='20em')
        fb.field('version',width='4em')
        fb.checkbox(value='^mainbc.regions.left?show',label='!!Show fields')     
        tc = bc.tabContainer(region='center',nodeId='doc_tabs',selectedPage='^doc_tabs.selectedPage')
        editorPane = tc.contentPane(title='Edit',pageName='edit',id='editpage')
        bc.dataRpc('preview.pkeys','getPreviewPkeys',
                    maintable='^.maintable',_if='maintable',
                    _onResult="""
                                 var first_row = result[0];
                                 SET preview.selected_id = first_row; 
                                 SET preview.idx=0;
                                """
                    )
        #bc.dataController("console.log('record_id');console.log(record_id)",record_id="^preview.selected_id")
        
        self.previewPane(tc.borderContainer(title='Preview',pageName='view',_class='preview'))        
        self.metadataForm(tc.contentPane(title='!!Metadata',pageName='metadata',datapath='.metadata'),disabled=disabled)
        self.RichTextEditor(editorPane, value='^.content',height='100%',
                            toolbar=self.rte_toolbar_standard(),
                            config_contentsCss=self.getResourceUri('doctemplate.css',add_mtime=True))

    
    def previewPane(self,bc):
        top = bc.contentPane(region='top',overflow='hidden').toolbar()
        fb = top.formbuilder(cols=3, border_spacing='2px',visible='^form.record.maintable')
        fb.dbSelect(dbtable='^form.record.maintable',value='^preview.selected_id',
                    lbl='!!Record',width='20em')
        box = fb.div(width='70px')
        box.button('!!Previous', action='idx = idx>0?idx-1:10; SET preview.selected_id = pkeys[idx]; SET preview.idx = idx;', idx='=preview.idx',pkeys='=preview.pkeys',
                        iconClass="tb_button icnNavPrev",  showLabel=False)
        box.button('!!Next', action='idx = idx<=pkeys.length?idx+1:0; SET preview.selected_id = pkeys[idx]; SET preview.idx = idx;', idx='=preview.idx',pkeys='=preview.pkeys',
                        iconClass="tb_button icnNavNext", showLabel=False)
                        
        fb.dbSelect(dbtable='adm.htmltemplate',value='^html_template_id',
                    selected_name='html_template_name',lbl_width='10em',lbl='!!Template',
                    width='20em',hasDownArrow=True)
        fb.dataRpc('preview.renderedtemplate','renderTemplate',doctemplate='=form.record',record_id='^preview.selected_id',
                    templates='^html_template_name',_if='selectedTab=="view"&&doctemplate.getItem("content")',
                    selectedTab='^doc_tabs.selectedPage')
        
        bc.contentPane(region='center',padding='10px').div(height='100%',background='white').div(innerHTML='^preview.renderedtemplate')
                            
    def metadataForm(self,pane,disabled=None):
        fb = pane.formbuilder(cols=2, border_spacing='4px',fld_width='15em',disabled=disabled)
        fb.textbox(value='^.subject',lbl='Subject',colspan='2',width='100%')
        fb.textbox(value='^.to_address',lbl='To Address field')
        fb.textbox(value='^.from_address',lbl='From Address field')
        
    def html_item_res(self):
        return """<span><span class="tplfieldpath" fieldpath="'+treeItem.attr.fieldpath+'" itemtag = "'+treeItem.attr.tag+'">$'+treeItem.attr.fieldpath+'</span><span class="tplfieldcaption">'+treeItem.attr.caption+'</span></span><span>&nbsp</span>"""
        
    def left(self,pane):
        pane.dataRemote('.tree.fields','relationExplorer',table='^form.record.maintable',
                        dosort=False,caption='Fields')
        pane.tree(storepath='.tree',persist=False,
                     #inspect='shift', 
                     labelAttribute='caption',
                     _class='fieldsTree',
                     hideValues=True,
                     margin='6px',
                     font_size='.9em',
                     selected_fieldpath='.selpath',
                     draggable=True,
                     onDrag="""if(!(treeItem.attr.dtype && treeItem.attr.dtype!='RM' && treeItem.attr.dtype!='RO')){
                                    return false;
                                }
                                dragValues['text/html']='%s';
                                dragValues['text/plain'] =treeItem.attr.fieldpath;
                              """ %self.html_item_res(),                     
                     getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                     getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")
    
    def rpc_getPreviewPkeys(self,maintable=None):
        path = self.userStore().getItem('current.table.%s.last_selection_path' %maintable.replace('.','_'))
        selection = self.db.unfreezeSelection(path)
        if selection:
            result = selection.output('pkeylist')
        else:
            result = self.db.table(maintable).query(limit=10,order_by='$__ins_ts').selection().output('pkeylist')
        return "%s::JS" %str(result).replace("u'","'")

    def rpc_renderTemplate(self,doctemplate=None,record_id=None,templates=None,**kwargs):
        if not doctemplate['content']:
            return
        tplbuilder = self.tblobj.getTemplateBuilder(doctemplate=doctemplate,templates=templates)
        return self.tblobj.renderTemplate(tplbuilder,record_id=record_id,extraData=Bag(dict(host=self.request.host)))
        
        