# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-06-15.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='public:TableHandlerMain,foundation/macrowidgets:RichTextEditor'
    maintable='adm.doctemplate'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def windowTitle(self):
        return 'Doc Template Page'
         
    def th_form(self,form):
        bc = form.center.borderContainer()
        form.data('.tableTree', self.db.tableTreeBag(['sys'], omit=True, tabletype='main'))
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=3, border_spacing='4px')
        box = fb.field('maintable', width='15em', readOnly=True,validate_notnull=True) 
        box.menu(storepath='#FORM.tableTree', modifiers='*', _class='smallmenu', action='SET .maintable = $1.fullpath')
        fb.field('name', width='20em')
        fb.field('version', width='4em')
        tc = bc.tabContainer(region='center')
        self.editorPane(tc.borderContainer(title='Edit template'))
        self.previewPane(tc.borderContainer(title='Preview',datapath='.preview'))

    def editorPane(self,bc):
        bc.dataController("""console.log(maintable,bc)
                             genro.dom.setClass(bc._left,"visibleBcPane",maintable!=null); 
                             bc._layoutChildren("left");
                         """,maintable="^#FORM.record.maintable",bc=bc.js_widget)
        self.variableGrid(bc.borderContainer(region='left',width='260px',splitter=True,_class='hiddenBcPane'))
        self.RichTextEditor(bc.contentPane(region='center'), value='^#FORM.record.content', height='100%',
                            toolbar=self.rte_toolbar_standard())
        
    def variableGrid(self,bc):
        def struct(struct):
            r = struct.view().rows()
            r.cell('fieldname', name='Field', width='100%')
            r.cell('varname', name='As', width='10em')
        grid = self.includedGrid(bc.contentPane(region='bottom',height='30%'),nodeId='variables',storepath='#FORM.record.varsbag',
                                 del_action=True,label='!!Template Variables',struct=struct,datamode='bag')
        editor = grid.gridEditor()
        editor.textbox(gridcell='varname')
        grid.dragAndDrop(dropCodes='fielditem')
        grid.dataController("""console.log(data);
                                var caption = data.fullcaption;
                                var varname = caption.replace(/\W/g,'_').toLowerCase()
                                grid.addBagRow('#id', '*', grid.newBagRow({'fieldpath':data.fieldpath,fieldname:caption,varname:varname,virtual_column:data.virtual_column}));""",
                             data="^.dropped_fielditem",grid=grid.js_widget)
        
        treepane = bc.contentPane(region='center').div(position='absolute',top='3px',bottom='3px',left='3px',right='3px',overflow='auto')
        treepane.tree(storepath='.store',draggable=True,onDrag="""
                                if (!(treeItem.attr.dtype && treeItem.attr.dtype!='RM' && treeItem.attr.dtype!='RO')) {
                                    return false;
                                }
                                dragValues['text/plain'] = treeItem.attr.caption;
                                dragValues['fielditem'] = treeItem.attr;
                             """,labelAttribute='caption',hideValues=True,font_size='.9em',_class='fieldsTree',
                             getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                            getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")
          
        treepane.dataRemote('.store.fields', 'relationExplorer', 
                                   table='^#FORM.record.maintable',dosort=False, caption='Fields')
    



    def previewPane(self, bc):
        bc.dataRpc('.pkeys', 'getPreviewPkeys',
                   maintable='^.maintable', _if='maintable',_POST =True,
                   _onResult="""
                                 var first_row = result[0];
                                 SET preview.selected_id = first_row; 
                                 SET preview.idx=0;
                                """
                   )
        bar = bc.contentPane(region='top', overflow='hidden').slotToolbar('fb,*')
        fb = bar.fb.formbuilder(cols=3, border_spacing='0px', visible='^#FORM.record.maintable')
        fb.dbSelect(dbtable='^#FORM.record.maintable', value='^.selected_id',lbl='!!Record', width='20em')
        box = fb.div(width='70px')
        box.button('!!Previous',
                   action='idx = idx>0?idx-1:10; SET .selected_id = pkeys[idx]; SET .idx = idx;',
                   idx='=.idx', pkeys='=.pkeys',
                   iconClass="tb_button icnNavPrev", showLabel=False)
        box.button('!!Next',
                   action='idx = idx<=pkeys.length?idx+1:0; SET .selected_id = pkeys[idx]; SET .idx = idx;'
                   , idx='=.idx', pkeys='=.pkeys',
                   iconClass="tb_button icnNavNext", showLabel=False)

        fb.dbSelect(dbtable='adm.htmltemplate', value='^.html_template_id',
                    selected_name='.html_template_name', lbl_width='10em', lbl='!!Template',
                    width='20em', hasDownArrow=True)
                    
        fb.dataRpc('.renderedtemplate', 'renderTemplate', doctemplate='=#FORM.record',
                   _POST =True,record_id='^.selected_id',
                   templates='^.html_template_name', _if='doctemplate.getItem("content")')

        bc.contentPane(region='center', padding='10px').div(height='100%', background='white').div(innerHTML='^.renderedtemplate')

    def metadataForm(self, pane, disabled=None):
        fb = pane.formbuilder(cols=2, border_spacing='4px', fld_width='15em', disabled=disabled)
        fb.textbox(value='^.subject', lbl='Subject', colspan='2', width='100%')
        fb.textbox(value='^.to_address', lbl='To Address field')
        fb.textbox(value='^.from_address', lbl='From Address field')

    def html_item_res(self):
        return """<span><span class="tplfieldpath" fieldpath="'+treeItem.attr.fieldpath+'" itemtag = "'+treeItem.attr.tag+'">$'+treeItem.attr.fieldpath+'</span><span class="tplfieldcaption">'+treeItem.attr.caption+'</span></span><span>&nbsp</span>"""

    def left(self, pane):
        pane.dataRemote('.tree.fields', 'relationExplorer', table='^#FORM.record.maintable',
                        dosort=False, caption='Fields')
        pane.tree(storepath='.tree', persist=False,
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
                              """ % self.html_item_res(),
                  getLabelClass="""if (!node.attr.fieldpath && node.attr.table){return "tableTreeNode"}
                                        else if(node.attr.relation_path){return "aliasColumnTreeNode"}
                                        else if(node.attr.sql_formula){return "formulaColumnTreeNode"}""",
                  getIconClass="""if(node.attr.dtype){return "icnDtype_"+node.attr.dtype}
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""")

    def rpc_getPreviewPkeys(self, maintable=None):
        path = self.userStore().getItem('current.table.%s.last_selection_path' % maintable.replace('.', '_'))
        selection = self.db.unfreezeSelection(path)
        if selection:
            result = selection.output('pkeylist')
        else:
            result = self.db.table(maintable).query(limit=10, order_by='$__ins_ts').selection().output('pkeylist')
        return "%s::JS" % str(result).replace("u'", "'")

    def rpc_renderTemplate(self, doctemplate=None, record_id=None, templates=None, **kwargs):
        if not doctemplate['content']:
            return
        tplbuilder = self.tblobj.getTemplateBuilder(doctemplate=doctemplate, templates=templates)
        return self.tblobj.renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)))
        