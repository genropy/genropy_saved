# -*- coding: UTF-8 -*-

# template_maker.py
# Created by Francesco Porcari on 2011-06-20.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires='foundation/includedview,foundation/macrowidgets:RichTextEditor'
    css_requires='public'
         
    def main(self, root, **kwargs):
        callArgs = self.getCallArgs('pkg','table','tplname','renderpkey')    
        pkg = pkg=callArgs.get('pkg')
        table = callArgs.get('table')
        form = root.frameForm(frameCode='doctemplate',datapath='main')
        maintable = '%s.%s' %(pkg,table)
        tplname = callArgs.get('tplname')
        #startPath = self.getResourcePath('tables/%s/tpl/%s' %(table,tplname), ext='xml',pkg=pkg) if tplname else '*newrecord*'
        startPath = self.site.getStatic('pkg').path(pkg,'tables',table,'tpl',tplname,folder='resources')
        startPath = '%s.xml' %startPath
        form.data('.record?maintable',maintable)
        form.data('main.renderpkey',callArgs.get('renderpkey'))
        store = form.formStore(handler='document',startKey=startPath)
        store.handler('load',maintable=maintable,defaultCb="""function(kw){
            var b = new gnr.GnrBag();
            b.setItem('content',new gnr.GnrBag(),{maintable:kw.maintable});
            return b.popNode('content');
        }""")
        
        toolbar = form.top.slotToolbar(slots='lcol,*,rcol')
        bc = form.center.borderContainer()
        toolbar.lcol.slotButton('Fields',action='bc.setRegionVisible("left","toggle");',bc=bc.js_widget)
        toolbar.rcol.slotButton('Preview',action='bc.setRegionVisible("right","toggle");',bc=bc.js_widget)
        leftbc = bc.borderContainer(region='left',width='300px',hidden=True)
        self.fieldstree(leftbc.contentPane(region='top',height='50%',datapath='.fields',splitter=True,_class='pbl_roundedGroup',margin='3px'))
        self.varsgrid(leftbc.contentPane(region='center',margin='3px',margin_top='4px'))
        self.previewpane(bc.framePane(region='right',hidden=True,width='600px'))
        self.RichTextEditor(bc.contentPane(region='center'),value='^#FORM.record.source')
        
    def rpc_pippo(self,record):
        pass
        
    def fieldstree(self,pane):
        pane.tree(storepath='.store',draggable=True,onDrag="""
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
                                     else {return opened?'dijitFolderOpened':'dijitFolderClosed'}""",_fired='^#FORM.record.maintable')
        pane.dataRemote('.store.fields', 'relationExplorer', table='^#FORM.record?maintable',dosort=False, caption='Fields')
    
    def varsgrid(self,bc):
        def struct(struct):
            r = struct.view().rows()
            r.cell('fieldname', name='Field', width='100%')
            r.cell('varname', name='As', width='10em')
        grid = self.includedGrid(bc,nodeId='variables',storepath='#FORM.record.varsbag',
                                 del_action=True,label='!!Template Variables',struct=struct,datamode='bag')
        editor = grid.gridEditor()
        editor.textbox(gridcell='varname')
        grid.dragAndDrop(dropCodes='fielditem')
        grid.dataController("""var caption = data.fullcaption;
                                var varname = caption.replace(/\W/g,'_').toLowerCase()
                                grid.addBagRow('#id', '*', grid.newBagRow({'fieldpath':data.fieldpath,fieldname:caption,varname:varname,virtual_column:data.virtual_column}));""",
                             data="^.dropped_fielditem",grid=grid.js_widget)
    
    def previewpane(self,frame):
        frame.dataRpc('.pkeys', 'getPreviewPkeys',
                   maintable='^#FORM.record?maintable', _if='maintable',_POST =True,
                   _onResult="""
                                 var first_row = result[0];
                                 SET .selected_id = first_row; 
                                 SET .idx=0;
                                """
                   )
        bar = frame.top.slotToolbar('prev,next,fb,*')
        footer = frame.bottom.slotBar('*,zoom')
        bar.prev.slotButton('!!Previous',
                   action='idx = idx>0?idx-1:10; SET .selected_id = pkeys[idx]; SET .idx = idx;',
                   idx='=.idx', pkeys='=.pkeys',
                   iconClass="tb_button icnNavPrev", showLabel=False)
        bar.next.slotButton('!!Next',
                   action='idx = idx<=pkeys.length?idx+1:0; SET .selected_id = pkeys[idx]; SET .idx = idx;'
                   , idx='=.idx', pkeys='=.pkeys',
                   iconClass="tb_button icnNavNext", showLabel=False)
        fb = bar.fb.formbuilder(cols=2, border_spacing='0px', visible='^#FORM.record?maintable')
        fb.dbSelect(dbtable='^#FORM.record?maintable', value='^.selected_id',lbl='!!Record', width='10em')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.html_template_id',
                    selected_name='.html_template_name', lbl='!!Template',
                    width='10em', hasDownArrow=True)
                    
        fb.dataRpc('.renderedtemplate', 'renderTemplate', templatepath='=#FORM.pkey',
                   _POST =True,record_id='^.selected_id',templates='^.html_template_name', _if='templatepath')
        
        footer.zoom.data('.zoomFactor',.5)
        footer.zoom.horizontalSlider(value='^.zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True, width='15em')
        frame.div(innerHTML='^.renderedtemplate',zoomFactor='^.zoomFactor')


    def rpc_getPreviewPkeys(self, maintable=None):
        path = self.userStore().getItem('current.table.%s.last_selection_path' % maintable.replace('.', '_'))
        selection = self.db.unfreezeSelection(path)
        if selection:
            result = selection.output('pkeylist')
        else:
            result = self.db.table(maintable).query(limit=10, order_by='$__ins_ts').selection().output('pkeylist')
        return "%s::JS" % str(result).replace("u'", "'")

    def rpc_renderTemplate(self, templatepath=None, record_id=None, templates=None, **kwargs):
        return
        doctemplate = self.db.table('adm.doctemplate').record(pkey=doctemplate_id).output('bag')
        templatebag = doctemplate['templatebag']
        if not templatebag:
            return
        tplbuilder = self.tblobj.getTemplateBuilder(templatebag=templatebag, templates=templates)
        return self.tblobj.renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)))
