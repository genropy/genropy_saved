# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag
import re
from StringIO import StringIO
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbaghtml import BagToHtml
import lxml.html as ht

TEMPLATEROW = re.compile(r"<!--TEMPLATEROW:(.*?)-->")

class TemplateEditorBase(BaseComponent):
    @public_method
    def te_getPreviewPkeys(self, maintable=None):
        path = self.userStore().getItem('current.table.%s.last_selection_path' % maintable.replace('.', '_'))
        selection = self.db.unfreezeSelection(path)
        if selection:
            result = selection.output('pkeylist')
        else:
            result = self.db.table(maintable).query(limit=10, order_by='$__ins_ts').selection().output('pkeylist')
        return "%s::JS" % str(result).replace("u'", "'")
    
    @public_method
    def te_getPreview(self, record_id=None, compiled=None, templates=None,template_id=None,**kwargs):
        if template_id:
            templates = self.db.table('adm.htmltemplate').readColumns(columns='$name',pkey=template_id)
        tplbuilder = self.getTemplateBuilder(compiled=compiled, templates=templates)
        return self.renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)))

    
    def getTemplateBuilder(self, compiled=None, templates=None):
        htmlbuilder = BagToHtml(templates=templates, templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        htmlbuilder.doctemplate = compiled
        htmlbuilder.virtual_columns = compiled.getItem('main?virtual_columns')
        htmlbuilder.locale = compiled.getItem('main?locale')
        htmlbuilder.formats = compiled.getItem('main?formats')
        htmlbuilder.masks = compiled.getItem('main?masks')
        htmlbuilder.df_templates = compiled.getItem('main?df_templates')
        htmlbuilder.data_tblobj = self.db.table(compiled.getItem('main?maintable'))
        return htmlbuilder
        
    def renderTemplate(self, templateBuilder, record_id=None, extraData=None, locale=None,**kwargs):
        record = Bag()
        if record_id:
            record = templateBuilder.data_tblobj.record(pkey=record_id,
                                                        virtual_columns=templateBuilder.virtual_columns).output('bag')
        if extraData:
            record.update(extraData)
        locale = locale or templateBuilder.locale
        formats = templateBuilder.formats or dict()
        masks = templateBuilder.masks or dict()
        df_templates = templateBuilder.df_templates or dict()
        record.setItem('_env_', Bag(self.db.currentEnv))
        #record.setItem('_template_', templateBuilder.doctemplate_info)
        body = templateBuilder(htmlContent=templateReplace(templateBuilder.doctemplate,record, safeMode=True,noneIsBlank=False,locale=locale, formats=formats,masks=masks,df_templates=df_templates,localizer=self.localizer),
                            record=record,**kwargs)
        return body
    
    def te_compileBagForm(self,table=None,sourcebag=None,varsbag=None,parametersbag=None,record_id=None,templates=None):
        result = Bag()
        varsdict = dict()
        for varname,fieldpath in varsbag.digest('#v.varname,#v.fieldpath'):
            varsdict[varname] = '$%s' %fieldpath
        for k,v in sourcebag.items():
            if v:
                result[k] = templateReplace(v, varsdict, True,False)
        return result
            
        
    @public_method
    def te_compileTemplate(self,table=None,datacontent=None,varsbag=None,parametersbag=None,record_id=None,templates=None,template_id=None):
        result = Bag()
        formats = dict()
        masks = dict()
        df_templates = dict()
        columns = []
        virtual_columns = []
        varsdict = dict()
        if varsbag:
            tplvars =  varsbag.digest('#v.varname,#v.fieldpath,#v.virtual_column,#v.format,#v.mask,#v.df_template')
            for varname,fldpath,virtualcol,format,mask,df_template in tplvars:
                fk=''
                if format:
                    fk=varname
                    formats[varname] = format
                if mask:
                    fk=varname
                    masks[varname] = mask
                if df_template:
                    fk=varname
                    df_templates[varname] = df_template
                if fk:
                    fk='^%s'%fk
                varsdict[varname] = '$%s%s' %(fldpath,fk)
                
                columns.append(fldpath)
                if virtualcol:
                    virtual_columns.append(fldpath)
        if parametersbag:
            tplpars = parametersbag.digest('#v.code,#v.format,#v.mask')
            for code,format,mask in tplpars:
                formats[code] = format
                masks[code] = mask
        template = templateReplace(datacontent, varsdict, True,False)
        compiled = Bag()
        doc = ht.parse(StringIO(template)).getroot()
        htmltables = doc.xpath('//table')
        for t in htmltables:
            attributes = t.attrib
            if 'row_datasource' in attributes:
                subname = attributes['row_datasource']
                tbody = t.xpath('tbody')[0]
                tbody_lastrow = tbody.getchildren()[-1]
                tbody.replace(tbody_lastrow,ht.etree.Comment('TEMPLATEROW:$%s' %subname))
                subtemplate=ht.tostring(tbody_lastrow).replace('%s.'%subname,'')
                compiled.setItem(subname.replace('.','_'),subtemplate)
        compiled.setItem('main', TEMPLATEROW.sub(lambda m: '\n%s\n'%m.group(1),ht.tostring(doc)),
                            maintable=table,locale=self.locale,virtual_columns=','.join(virtual_columns),
                            columns=','.join(columns),formats=formats,masks=masks,df_templates=df_templates)
        result.setItem('compiled',compiled)
        if record_id:
            result.setItem('preview',self.te_getPreview(compiled=compiled,record_id=record_id,templates=templates,template_id=template_id))
        return result

class TemplateEditor(TemplateEditorBase):
    py_requires='foundation/macrowidgets:RichTextEditor,gnrcomponents/framegrid:FrameGrid'
    css_requires='public'
    @struct_method
    def te_templateEditor(self,pane,storepath=None,maintable=None,**kwargs):
        sc = self._te_mainstack(pane,table=maintable)
        self._te_frameInfo(sc.framePane(title='!!Metadata',pageName='info',childname='info'),table=maintable)
        self._te_frameEdit(sc.framePane(title='!!Edit',pageName='edit',childname='edit'))
        self._te_framePreview(sc.framePane(title='!!Preview',pageName='preview',childname='preview'),table=maintable)
        #self._te_frameHelp(sc.framePane(title='!!Help',pageName='help',childname='help'))
        
        return sc
    
    def _te_mainstack(self,pane,table=None):
        sc = pane.stackContainer(selectedPage='^.status',_anchor=True)
        sc.dataRpc('dummy',self.te_compileTemplate,varsbag='=.data.varsbag',parametersbag='=.data.parameters',
                    datacontent='=.data.content',table=table,_if='_status=="preview"&&datacontent&&varsbag',
                    _status='^.status',record_id='=.preview.selected_id',templates='=.preview.html_template_name',
                    _onResult="""
                    SET .data.compiled = result.getItem('compiled').deepCopy();
                    SET .preview.renderedtemplate = result.getItem('preview');
                    var curr_letterehead =GET .preview.letterhead_id;
                    if(!curr_letterehead){
                        SET .preview.letterhead_id = GET .data.metadata.default_letterhead;
                    }
                    """)
        return sc
    
    def _te_varsgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname', name='Field', width='100%')
        r.cell('varname', name='As', width='15em')
        r.cell('format', name='Format', width='10em')
        r.cell('mask', name='Mask', width='20em')

    def _te_info_top(self,pane):
        fb = pane.div(margin='5px').formbuilder(cols=5, border_spacing='4px',fld_width='100%',width='100%',
                                                tdl_width='6em',datapath='.data.metadata')
        fb.textbox(value='^.author',lbl='!!Author',tdf_width='20em')
        fb.numberTextBox(value='^.version',lbl='!!Version')
        fb.dateTextBox(value='^.date',lbl='!!Date')
        fb.checkbox(value='^.is_print',label='!!Print')
        fb.checkbox(value='^.is_mail',label='!!Mail')
        fb.dataController("""var result = [];
                             if(is_mail){result.push('is_mail');}
                             if(is_print){result.push('is_print');}
                             if(flags){result.push(flags);}
                             SET #ANCHOR.userobject_meta.flags = result.join(',');""",
                        is_mail="^.is_mail",is_print='^.is_print',flags='^.flags')
        fb.dbSelect(value='^.default_letterhead',dbtable='adm.htmltemplate',
                    lbl='!!Letterhead',hasDownArrow=True)
        fb.textbox(value='^.summary',lbl='!!Summary',colspan=4)
        if self.isDeveloper():
            fb.textbox(value='^.flags',lbl='!!Flags',colspan=5)
    
    @extract_kwargs(fieldsTree=dict(slice_prefix=False))
    def _te_info_vars(self,bc,table=None,datasourcepath=None,fieldsTree_kwargs=None,**kwargs):
        frame = bc.frameGrid(datapath='.varsgrid',
                                storepath='#ANCHOR.data.varsbag',
                                struct=self._te_varsgrid_struct,
                                datamode='bag',splitter=True,**kwargs)
        frame.left.slotBar('5,fieldsTree,*',
                            fieldsTree_table=table,
                            fieldsTree_dragCode='fieldvars',
                            closable=True,width='150px',fieldsTree_height='100%',splitter=True,**fieldsTree_kwargs)
        grid = frame.grid
        editor = grid.gridEditor()
        editor.textbox(gridcell='varname')
        editor.textbox(gridcell='format')
        editor.textbox(gridcell='mask')
        frame.top.slotToolbar(slots='gridtitle,*,delrow',gridtitle='!!Variables')
        grid.dragAndDrop(dropCodes='fieldvars')
        grid.dataController("""var caption = data.fullcaption;
                                var varname = caption.replace(/\W/g,'_').toLowerCase();
                                var df_template =null;

                                var fieldpath = data.fieldpath;
                                
                                if(fieldpath.indexOf(':')>=0){
                                    fieldpath = fieldpath.split(':');
                                    df_template = fieldpath[1];
                                    fieldpath = fieldpath[0];
                                }
                                
                                grid.addBagRow('#id', '*', grid.newBagRow({'fieldpath':fieldpath,fieldname:caption,varname:varname,virtual_column:data.virtual_column,df_template:df_template}));""",
                             data="^.dropped_fieldvars",grid=grid.js_widget)    
    
    def _te_info_parameters(self,bc,**kwargs):
        frame = bc.frameGrid(datamode='bag',datapath='.parametersgrid',
                                storepath='#ANCHOR.data.parameters', 
                                struct=self._te_parameters_struct,
                                selfDragRows=True,**kwargs)
        frame.top.slotToolbar('gridtitle,*,addrow,delrow',gridtitle='!!Parameters')
        gridEditor = frame.grid.gridEditor()
        gridEditor.textbox(gridcell='code')
        gridEditor.textbox(gridcell='description')
        gridEditor.filteringSelect(gridcell='fieldtype',values='!!T:Text,L:Integer,D:Date,N:Decimal,B:Boolean,TL:Long Text')
        gridEditor.textbox(gridcell='format')      
        gridEditor.textbox(gridcell='mask') 
        gridEditor.textbox(gridcell='values') 
        
    def _te_frameInfo(self,frame,table=None):
        frame.top.slotToolbar('5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        bc = frame.center.borderContainer(margin='2px',_class='pbl_roundedGroup')
        self._te_info_top(bc.contentPane(region='top'))
        self._te_info_vars(bc,table=table,region='bottom',height='60%')
        self._te_info_parameters(bc,region='center')
        
    def _te_pickers(self,tc):
        tc.dataController("""var result = new gnr.GnrBag();
                            var varfolder= new gnr.GnrBag();
                            var parsfolder = new gnr.GnrBag();
                            var attrs,varname;
                            varsbag.forEach(function(n){
                                varname = n._value.getItem('varname');
                                varfolder.setItem(n.label,null,{caption:n._value.getItem('fieldname'),code:varname});
                            },'static');
                            result.setItem('variables',varfolder,{caption:varcaption})
                            if (parameters){
                                parameters.forEach(function(n){
                                    attrs = n.attr;
                                    parsfolder.setItem(n.label,null,{caption:attrs.description || attrs.code,code:attrs.code})
                                },'static');
                                result.setItem('pars',parsfolder,{caption:parscaption})
                            }
                            SET .allvariables = result;
                            FIRE .tree_rebuild;""",
            varsbag="=.data.varsbag",parameters='=.data.parameters',
            varcaption='!!Fields',parscaption='!!Parameters',_if='status=="edit"',status='^.status')
        vartab = tc.contentPane(title='Variables',overflow='auto',text_align='left',margin='2px',_class='pbl_roundedGroup')
        vartab.tree(storepath='.allvariables',_fired='^.tree_rebuild',onDrag="dragValues['text/plain'] = '$'+treeItem.attr.code;",
                hideValues=True,draggable=True,_class='fieldsTree',labelAttribute='caption')
        if 'flib' in self.db.packages:
            self.mixinComponent('flib:FlibPicker')
            tc.contentPane(title='!!Files').flibPickerPane(viewResource=':ImagesView',preview=False,gridpane_region='center', gridpane_margin='2px',
                            treepane_region='top',treepane_margin='2px',treepane_splitter=True,
                            treepane__class='pbl_roundedGroup',treepane_height='30%')

        
        
    def _te_frameEdit(self,frame):
        frame.top.slotToolbar(slots='5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        bc = frame.center.borderContainer(design='sidebar')
        self._te_pickers(frame.tabContainer(region='left',width='200px',splitter=True))                
        frame.dataController("bc.setRegionVisible('top',mail)",bc=bc.js_widget,mail='^.data.metadata.is_mail',_if='mail!==null')
        top = bc.contentPane(region='top',datapath='.data.metadata.email',hidden=True,margin='2px',_class='pbl_roundedGroup')
        top.div("!!Email metadata",_class='pbl_roundedGroupLabel')
        fb = top.div(margin_right='15px').formbuilder(cols=1, border_spacing='2px',width='100%',fld_width='100%',tdl_width='8em')
        fb.textbox(value='^.subject', lbl='!!Subject',dropTypes = 'text/plain')
        fb.textbox(value='^.to_address', lbl='!!To',dropTypes = 'text/plain')
        fb.textbox(value='^.cc_address', lbl='!!CC',dropTypes = 'text/plain')
        self.RichTextEditor(bc.contentPane(region='center'), value='^.data.content',
                            toolbar='standard')
                            
    def _te_framePreview(self,frame,table=None):
        bar = frame.top.slotToolbar('5,parentStackButtons,10,fb,*',parentStackButtons_font_size='8pt')                   
        fb = bar.fb.formbuilder(cols=2, border_spacing='0px',margin_top='2px')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.preview.letterhead_id',
                    selected_name='.preview.html_template_name',lbl='!!Letterhead',
                    width='10em', hasDownArrow=True)
        fb.dbSelect(dbtable=table, value='^.preview.selected_id',lbl='!!Record', width='12em',lbl_width='6em')
        fb.dataRpc('.preview.renderedtemplate', self.te_getPreview,
                   _POST =True,record_id='^.preview.selected_id',
                   templates='^.preview.html_template_name',
                   compiled='=.data.compiled')
        frame.center.contentPane(margin='5px',background='white',border='1px solid silver',rounded=4,padding='4px').div('^.preview.renderedtemplate')

    # def _te_frameHelp(self,frame):
    #     frame.top.slotToolbar(slots='5,parentStackButtons,*',parentStackButtons_font_size='8pt')
    #     bc = frame.center.borderContainer(design='sidebar')
    #     bc.div('Help')
        
    def _te_parameters_struct(self,struct):
        r = struct.view().rows()
        r.cell('code', name='!!Code', width='10em')
        r.cell('description', name='!!Description', width='40em')
        r.cell('fieldtype', name='!!Fieldtype', width='10em')
        r.cell('format', name='!!Format', width='10em')
        r.cell('mask', name='!!Mask', width='15em')
        r.cell('values', name='!!Values', width='100%')    

class PaletteTemplateEditor(TemplateEditor):
    @struct_method
    def te_paletteTemplateEditor(self,pane,paletteCode=None,maintable=None,**kwargs):
        palette = pane.palettePane(paletteCode=paletteCode or 'template_manager',
                                    title='^.caption',
                                    width='750px',height='500px',**kwargs)
        sc = palette.templateEditor(maintable=maintable)
        infobar = sc.info.top.bar
        infobar.replaceSlots('#','#,menutemplates,deltpl,savetpl,5')
        infobar.deltpl.slotButton('!!Delete current',iconClass='iconbox trash',
                                action='FIRE .deleteCurrent',disabled='^.currentTemplate.pkey?=!#v')
        infobar.dataController('SET .currentTemplate.path="__newtpl__";',_onStart=True)
        infobar.dataFormula(".palette_caption", "prefix+caption",caption="^.caption",prefix='!!Edit ')
        infobar.menutemplates.div(_class='iconbox folder').menu(modifiers='*',storepath='.menu',
                action="""SET .currentTemplate.pkey=$1.pkey;
                          SET .currentTemplate.mode = $1.tplmode;
                          SET .currentTemplate.path = $1.fullpath;""",_class='smallmenu')
        infobar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate',
                                disabled='^.data.content?=!#v')
        
        editbar = sc.edit.top.bar
        editbar.replaceSlots('#','#,savetpl,5')
        editbar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate',
                                disabled='^.data.content?=!#v')
        
        previewbar = sc.preview.top.bar
        previewbar.replaceSlots('#','#,savetpl,5')
        previewbar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate',
                                disabled='^.data.content?=!#v')
        
        
        infobar.dataController("""
            var editorbag = this.getRelativeData();
            if(tplpath=='__newtpl__'){
                editorbag.setItem('data',new gnr.GnrBag());
                editorbag.setItem('data.metadata.author',user);
                editorbag.setItem('userobject_meta',new gnr.GnrBag());
                editorbag.setItem('caption',newcaption);
            }else if(pkey){
                genro.serverCall('_table.adm.userobject.loadUserObject',{table:table,pkey:pkey},function(result){
                    editorbag.setItem('data',result._value.deepCopy());
                    editorbag.setItem('mode','userobject');
                    editorbag.setItem('caption',result.attr.description || result.attr.code);
                    editorbag.setItem('userobject_meta',new gnr.GnrBag(result.attr));
                },null,'POST')
            }
        """,tplpath="^.currentTemplate.path",tplmode='=.currentTemplate.tplmode',
                pkey='=.currentTemplate.pkey',table=maintable,newcaption='!!New template',user=self.user)
        infobar.dataRpc('dummy',self.db.table('adm.userobject').deleteUserObject,table=maintable,pkey='=.currentTemplate.pkey',
                        _onResult='SET .currentTemplate.path="__newtpl__";',_fired='^.deleteCurrent')
        infobar.dataController("""
            if(currentTemplatePkey){
                FIRE .save_userobject = currentTemplatePkey;
            }else{
                FIRE .save_userobject = '*newrecord*';
            }
        """,_fired='^.savetemplate',currentTemplateMode='=.currentTemplate.tplmode',
                            currentTemplatePath='=.currentTemplate.path',
                            currentTemplatePkey='=.currentTemplate.pkey',
                            data='=.data')
        infobar.dataController("""
                var that = this;
                var savepath = this.absDatapath('.userobject_meta');
                var kw = {'tplmode':'userobject','table':table,
                        'data':data,metadata:'='+savepath}                
                genro.dev.userObjectDialog(_T('Save Template'),savepath,
                function(dialog) {
                    genro.serverCall('te_saveTemplate',kw,
                        function(result) {
                            that.setRelativeData('.currentTemplate.pkey',result['id']);
                            that.setRelativeData('.currentTemplate.path',result['code']);
                            dialog.close_action();
                        },null,'POST');
            });
            """,pkey='^.save_userobject',data='=.data',table=maintable)
        infobar.dataRemote('.menu',self.te_menuTemplates,table=maintable,cacheTime=5)
        
    @public_method
    def te_menuTemplates(self,table=None):
        result = Bag()
        #from_resources = None #todo
        from_userobject = self.db.table('adm.userobject').userObjectMenu(table,'template') #todo
        from_doctemplate = Bag()
        f = self.db.table('adm.doctemplate').query(where='$maintable=:t',t=table).fetch()
        for r in f:
            from_doctemplate.setItem(r['pkey'],None,caption=r['name'],tplmode='doctemplate',pkey=r['pkey'])
        result.update(from_doctemplate)
        for n in from_userobject:
            result.setItem(n.label,None,tplmode='userobject',**n.attr)
        result.setItem('__newtpl__',None,caption='!!New Template')
        return result

    @public_method
    def te_saveTemplate(self,pkey=None,data=None,tplmode=None,table=None,metadata=None,**kwargs):
        record = None
        if tplmode=='doctemplate':
            tblobj = self.db.table('adm.doctemplate')
            record = tblobj.record(for_update=True,pkey=pkey).output('dict')
            record['varsbag'] = data['varsbag']
            record['content'] = data['content']
            tblobj.update(record)
            self.db.commit()
        elif tplmode == 'userobject':
            if data['metadata.email']:
                data['metadata.email_compiled'] = self.te_compileBagForm(table=table,sourcebag=data['metadata.email'],varsbag=data['varsbag'],parametersbag=data['parameters'])
            data['compiled'] = self.te_compileTemplate(table=table,datacontent=data['content'],varsbag=data['varsbag'],parametersbag=data['parameters'])['compiled']
            pkey,record = self.db.table('adm.userobject').saveUserObject(table=table,metadata=metadata,data=data,objtype='template')
            record.pop('data')
        return record
        
class ChunkEditor(PaletteTemplateEditor):
    @public_method
    def te_chunkEditorPane(self,pane,table=None,resource_mode=None,paletteId=None,datasourcepath=None,**kwargs):
        sc = self._te_mainstack(pane,table=table)
        self._te_frameChunkInfo(sc.framePane(title='!!Metadata',pageName='info',childname='info'),table=table,datasourcepath=datasourcepath)
        bar = sc.info.top.bar
        bar.replaceSlots('#','#,customres,savetpl,5')
        if resource_mode:
            bar.customres.checkbox(value='^.data.metadata.custom',label='!!Custom')
        else:
            bar.customres.div()
        self._te_saveButton(bar.savetpl,table,paletteId)
        frameEdit = sc.framePane(title='!!Edit',pageName='edit',childname='edit')
        self._te_frameEdit(frameEdit)
        bar = frameEdit.top.bar
        bar.replaceSlots('#','#,savetpl,5')
        self._te_saveButton(bar.savetpl,table,paletteId)
        framePreview = sc.framePane(title='!!Preview',pageName='preview',childname='preview')
        self._te_framePreviewChunk(framePreview,table=table,datasourcepath=datasourcepath)
        bar = framePreview.top.bar
        bar.replaceSlots('#','#,savetpl,5')
        self._te_saveButton(bar.savetpl,table,paletteId)
        
    def _te_frameChunkInfo(self,frame,table=None,datasourcepath=None):
        frame.top.slotToolbar('5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        bc = frame.center.borderContainer(margin='2px',_class='pbl_roundedGroup')
        self._te_info_vars(bc,table=table,region='center',
                            fieldsTree_currRecordPath=datasourcepath,
                            fieldsTree_explorerPath='#ANCHOR.dbexplorer')
        #self._te_info_parameters(bc,region='center')
    
    def _te_framePreviewChunk(self,frame,table=None,datasourcepath=None):
        bar = frame.top.slotToolbar('5,parentStackButtons,10,fb,*',parentStackButtons_font_size='8pt')                   
        fb = bar.fb.formbuilder(cols=1, border_spacing='0px',margin_top='2px')
        if not datasourcepath:
            fb.dbSelect(dbtable='adm.htmltemplate', value='^.preview.letterhead_id',
                    selected_name='.preview.html_template_name',lbl='!!Letterhead',
                    width='10em', hasDownArrow=True)
            preview_id = '.preview.selected.id'
        else:
            preview_id = '%s.%s' %(datasourcepath,self.db.table(table).pkey)
        record_id = '^%s' %preview_id
        frame.dataRpc('.preview.renderedtemplate', self.te_getPreview,
                   _POST =True,record_id=record_id,_status='^.status',_if='compiled && _status=="preview"',_else='return new gnr.GnrBag()',
                   compiled='=.data.compiled')
        frame.center.contentPane(margin='5px',background='white',border='1px solid silver',rounded=4,padding='4px').div('^.preview.renderedtemplate')

        
        
    def _te_saveButton(self,pane,table,paletteId):
        pane.slotButton('!!Save',action="""var result = genro.serverCall('te_compileTemplate',{table:table,datacontent:dc,varsbag:vb,parametersbag:pb},null,null,'POST');
                                    data.setItem('compiled',result.getItem('compiled'));
                                    genro.nodeById(paletteId).publish("savechunk");""",
                            iconClass='iconbox save',paletteId=paletteId,table=table,dc='=.data.content',
                            vb='=.data.varsbag',pb='=.data.parametersbag',data='=.data')
        
    
        
