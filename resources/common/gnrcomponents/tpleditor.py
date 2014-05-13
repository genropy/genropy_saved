# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent,TableScriptToHtml
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag
from StringIO import StringIO
from gnr.core.gnrstring import templateReplace
#from gnr.core.gnrbaghtml import BagToHtml
HT = None
TEMPLATEROW = None
try:
    import lxml.html as HT
    import re
    TEMPLATEROW = re.compile(r"<!--TEMPLATEROW:(.*?)-->")
except:
    pass



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
    def te_getPreview(self, record_id=None, compiled=None,templates=None,template_id=None,**kwargs):
        if template_id:
            templates = self.db.table('adm.htmltemplate').readColumns(columns='$name',pkey=template_id)
        tplbuilder = self.te_getTemplateBuilder(compiled=compiled, templates=templates)
        return self.te_renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)))

    @public_method
    def te_renderChunk(self, record_id=None,template_address=None,templates=None,template_id=None,**kwargs):
        data,dataInfo = self.loadTemplate(template_address=template_address,asSource=True)
        if not data:
            return '<div class="chunkeditor_emptytemplate">Template not yet created</div>',dataInfo
        compiled = data['compiled']
        result = Bag()
        if not compiled:
            content = data['content']
            record = self.db.table(template_address.split(':')[0]).recordAs(record_id)
            result['rendered'] = templateReplace(content,record)
            result['template_data'] = data
            return result,dataInfo
        tplbuilder = self.te_getTemplateBuilder(compiled=compiled, templates=templates)
        result['rendered'] = self.te_renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)),contentOnly=True)
        result['template_data'] = data
        return result,dataInfo
    
    def te_getTemplateBuilder(self, compiled=None, templates=None):
        tblobj = self.db.table(compiled.getItem('main?maintable'))
        htmlbuilder = TableScriptToHtml(page=self,templates=templates, resource_table=tblobj,templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        htmlbuilder.doctemplate = compiled
        htmlbuilder.virtual_columns = compiled.getItem('main?virtual_columns')
        htmlbuilder.locale = compiled.getItem('main?locale')
        htmlbuilder.formats = compiled.getItem('main?formats')
        htmlbuilder.masks = compiled.getItem('main?masks')
        htmlbuilder.editcols = compiled.getItem('main?editcols')
        htmlbuilder.df_templates = compiled.getItem('main?df_templates')
        htmlbuilder.dtypes = compiled.getItem('main?dtypes')
        htmlbuilder.data_tblobj = tblobj
        return htmlbuilder
        
    def te_renderTemplate(self, templateBuilder, record_id=None, extraData=None, locale=None,contentOnly=False,**kwargs):
        record = Bag()
        if record_id:
            record = templateBuilder.data_tblobj.record(pkey=record_id,
                                                        virtual_columns=templateBuilder.virtual_columns).output('bag')
        else:
            record = templateBuilder.data_tblobj.record(pkey='*sample*',ignoreMissing=True,
                                                        virtual_columns=templateBuilder.virtual_columns).output('sample')
        if extraData:
            record.update(extraData)
        locale = locale or templateBuilder.locale
        formats = templateBuilder.formats or dict()
        masks = templateBuilder.masks or dict()
        editcols = templateBuilder.editcols or dict()

        df_templates = templateBuilder.df_templates or dict()
        dtypes = templateBuilder.dtypes or dict()

        record.setItem('_env_', Bag(self.db.currentEnv))
        #record.setItem('_template_', templateBuilder.doctemplate_info)
        htmlContent = templateReplace(templateBuilder.doctemplate,record, safeMode=True,noneIsBlank=False,locale=locale, 
                                                            formats=formats,masks=masks,editcols=editcols,df_templates=df_templates,
                                                            dtypes=dtypes,localizer=self.localizer,
                                                            urlformatter=self.externalUrl)
        if contentOnly:
            return htmlContent
        body = templateBuilder(htmlContent=htmlContent,
                            record=record,page_debug='silver',**kwargs)
        return body
    
    def te_compileBagForm(self,table=None,sourcebag=None,varsbag=None,parametersbag=None,record_id=None,templates=None):
        result = Bag()
        varsdict = dict()
        for varname,fieldpath in varsbag.digest('#v.varname,#v.fieldpath'):
            varsdict[varname] = '$%s' %fieldpath
        for k,v in sourcebag.items():
            if v:
                result[k] = templateReplace(v, varsdict, True,False,urlformatter=self.externalUrl)
        return result
            
        
    @public_method
    def te_compileTemplate(self,table=None,datacontent=None,varsbag=None,parametersbag=None,record_id=None,templates=None,template_id=None):
        result = Bag()
        formats = dict()
        editcols = dict()
        masks = dict()
        df_templates = dict()
        dtypes = dict()
        columns = []
        virtual_columns = []
        varsdict = dict()
        if varsbag:
            tplvars =  varsbag.digest('#v.varname,#v.fieldpath,#v.virtual_column,#v.required_columns,#v.format,#v.mask,#v.editable,#v.df_template,#v.dtype')
            for varname,fldpath,virtualcol,required_columns,format,mask,editable,df_template,dtype in tplvars:
                fk=''
                if format:
                    fk=varname
                    formats[varname] = format
                if mask:
                    fk=varname
                    masks[varname] = mask
                if editable:
                    fk=varname
                    editcols[varname] = editable
                if df_template:
                    fk=varname
                    df_templates[varname] = df_template
                if dtype:
                    dtypes[varname] = dtype
                if fk:
                    fk='^%s'%fk
                varsdict[varname] = '$%s%s' %(fldpath,fk)
                columns.append(fldpath)
                if virtualcol:
                    virtual_columns.append(fldpath)
                if required_columns:
                    prefix = '.'.join(fldpath.split('.')[0:-1])
                    for c in required_columns.split(','):
                        if not c in virtual_columns:
                            virtual_columns.append('%s.%s' %(prefix,c.replace('$','')) if prefix else c)
        if parametersbag:
            tplpars = parametersbag.digest('#v.code,#v.format,#v.mask')
            for code,format,mask in tplpars:
                formats[code] = format
                masks[code] = mask
        template = templateReplace(datacontent, varsdict, True,False,conditionalMode=False)
        compiled = Bag()
        cmain = template
        if HT:
            doc = HT.parse(StringIO(template)).getroot()
            htmltables = doc.xpath('//table')
            for t in htmltables:
                attributes = t.attrib
                if 'row_datasource' in attributes:
                    subname = attributes['row_datasource']
                    tbody = t.xpath('tbody')[0]
                    tbody_lastrow = tbody.getchildren()[-1]
                    tbody.replace(tbody_lastrow,HT.etree.Comment('TEMPLATEROW:$%s' %subname))
                    subtemplate=HT.tostring(tbody_lastrow).replace('%s.'%subname,'').replace('%24','$')
                    compiled.setItem(subname.replace('.','_'),subtemplate)
            cmain = TEMPLATEROW.sub(lambda m: '\n%s\n'%m.group(1),HT.tostring(doc).replace('%24','$'))
        compiled.setItem('main', cmain,
                            maintable=table,locale=self.locale,virtual_columns=','.join(virtual_columns),
                            columns=','.join(columns),formats=formats,masks=masks,editcols=editcols,df_templates=df_templates,dtypes=dtypes)
        result.setItem('compiled',compiled)
        if record_id:
            result.setItem('preview',self.te_getPreview(compiled=compiled,record_id=record_id,templates=templates,template_id=template_id))
        return result

class TemplateEditor(TemplateEditorBase):
    py_requires='gnrcomponents/framegrid:FrameGrid'
    css_requires='public'
    @struct_method
    def te_templateEditor(self,pane,storepath=None,maintable=None,editorConstrain=None,**kwargs):
        sc = self._te_mainstack(pane,table=maintable)
        self._te_frameInfo(sc.framePane(title='!!Metadata',pageName='info',childname='info'),table=maintable)
        self._te_frameEdit(sc.framePane(title='!!Edit',pageName='edit',childname='edit',editorConstrain=editorConstrain))
        self._te_framePreview(sc.framePane(title='!!Preview',pageName='preview',childname='preview'),table=maintable)
        #self._te_frameHelp(sc.framePane(title='!!Help',pageName='help',childname='help'))
        
        return sc
    
    def _te_mainstack(self,pane,table=None):
        sc = pane.stackContainer(selectedPage='^.status',_anchor=True)
        sc.dataRpc('dummy',self.te_compileTemplate,varsbag='=.data.varsbag',parametersbag='=.data.parameters',
                    datacontent='=.data.content',table=table,_if='_status=="preview"&&datacontent&&varsbag',
                    _POST=True,
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
        r.cell('fieldname', name='Field', width='20em',edit=True)
        r.cell('varname', name='As', width='15em',edit=True)
        r.cell('format', name='Format', width='10em',edit=True)
        r.cell('mask', name='Mask', width='20em',edit=True)
        if self.isDeveloper():
            r.cell('editable', name='!!Edit pars', width='20em',edit=True)


    def _te_info_top(self,pane):
        fb = pane.div(margin='5px').formbuilder(cols=7, border_spacing='4px',fld_width='100%',width='100%',
                                                tdl_width='5em',datapath='.data.metadata')
        fb.textbox(value='^.author',lbl='!!Author',tdf_width='12em')
        fb.numberTextBox(value='^.version',lbl='!!Version',width='4em')
        fb.dateTextBox(value='^.date',lbl='!!Date',width='6em')
        fb.checkbox(value='^.is_print',label='!!Print')
        fb.checkbox(value='^.is_mail',label='!!Mail')
        fb.checkbox(value='^.is_row',label='!!Row')
        fb.numberTextBox(value='^.row_height',width='3em',hidden='^.is_row?=!#v',lbl_hidden='^.is_row?=!#v',lbl='Height')
        fb.dataController("""var result = [];
                             if(is_mail){result.push('is_mail');}
                             if(is_print){result.push('is_print');}
                             if(is_row){result.push('is_row');}
                             if(flags){result.push(flags);}
                             SET #ANCHOR.userobject_meta.flags = result.join(',');""",
                        is_mail="^.is_mail",is_print='^.is_print',is_row='^.is_row',flags='^.flags')
        fb.dbSelect(value='^.default_letterhead',dbtable='adm.htmltemplate',
                    lbl='!!Letterhead',hasDownArrow=True,colspan=3)
        fb.textbox(value='^.summary',lbl='!!Summary',colspan=4)
        if self.isDeveloper():
            fb.textbox(value='^#ANCHOR.userobject_meta.flags',lbl='!!Flags',colspan=7)
    
    @extract_kwargs(fieldsTree=dict(slice_prefix=False))
    def _te_info_vars(self,bc,table=None,datasourcepath=None,fieldsTree_kwargs=None,**kwargs):
        frame = bc.bagGrid(datapath='.varsgrid',title='!!Variables',
                                storepath='#ANCHOR.data.varsbag',
                                struct=self._te_varsgrid_struct,
                                parentForm=False,
                                addrow=False,
                                splitter=True,**kwargs)
        frame.left.slotBar('5,fieldsTree,*',
                            fieldsTree_table=table,
                            fieldsTree_dragCode='fieldvars',
                            border_right='1px solid silver',
                            closable=True,width='150px',fieldsTree_height='100%',splitter=True,**fieldsTree_kwargs)
        grid = frame.grid
        grid.dragAndDrop(dropCodes='fieldvars')
        grid.dataController("""var caption = data.fullcaption;
                                var varname = caption.replace(/\W/g,'_').toLowerCase();
                                var df_template =null;

                                var fieldpath = data.fieldpath;
                                var dtype = data.dtype;
                                if(fieldpath.indexOf(':')>=0){
                                    fieldpath = fieldpath.split(':');
                                    df_template = fieldpath[1];
                                    fieldpath = fieldpath[0];
                                }
                                grid.gridEditor.addNewRows([{'fieldpath':fieldpath,
                                                                            dtype:dtype,
                                                                            fieldname:caption,
                                                                            varname:varname,
                                                                            virtual_column:data.virtual_column,
                                                                            required_columns:data.required_columns,
                                                                            df_template:df_template}]);""",
                             data="^.dropped_fieldvars",grid=grid.js_widget)    
    
    def _te_info_parameters(self,bc,**kwargs):
        bc.bagGrid(datapath='.parametersgrid',title='!!Parameters',
                                storepath='#ANCHOR.data.parameters', 
                                struct=self._te_parameters_struct,
                                parentForm=False,
                                selfDragRows=True,**kwargs)
        
    def _te_frameInfo(self,frame,table=None):
        frame.top.slotToolbar('5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        bc = frame.center.borderContainer()
        self._te_info_top(bc.contentPane(region='top'))
        self._te_info_vars(bc,table=table,region='bottom',height='60%')
        self._te_info_parameters(bc,region='center')
        
    def _te_pickers(self,tc):
        tc.dataController("""var result = new gnr.GnrBag();
                            var varfolder= new gnr.GnrBag();
                            var parsfolder = new gnr.GnrBag();
                            var attrs,varname;
                            varsbag.forEach(function(n){
                                n.delAttr('_newrecord');
                                n._value.popNode('_newrecord');
                                varname = n._value.getItem('varname');
                                varfolder.setItem(n.label,null,{caption:n._value.getItem('fieldname'),code:varname});
                            },'static');
                            result.setItem('variables',varfolder,{caption:varcaption})
                            if (parameters){
                                parameters.forEach(function(n){
                                    n.delAttr('_newrecord');
                                    n._value.popNode('_newrecord');
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
                hideValues=True,draggable=True,_class='fieldsTree',labelAttribute='code'
                )
        if 'flib' in self.db.packages:
            self.mixinComponent('flib:FlibPicker')
            tc.contentPane(title='!!Files').flibPickerPane(viewResource=':ImagesView',preview=False,gridpane_region='center', gridpane_margin='2px',
                            treepane_region='top',treepane_margin='2px',treepane_splitter=True,
                            treepane__class='pbl_roundedGroup',treepane_height='30%')

        
        
    def _te_frameEdit(self,frame,editorConstrain=None):
        frame.top.slotToolbar(slots='5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        bc = frame.center.borderContainer(design='sidebar')
        self._te_pickers(frame.tabContainer(region='left',width='200px',splitter=True))                
        frame.dataController("bc.setRegionVisible('top',mail)",bc=bc.js_widget,mail='^.data.metadata.is_mail',_if='mail!==null')
        top = bc.contentPane(region='top',datapath='.data.metadata.email',hidden=True,margin='2px',_class='pbl_roundedGroup')
        top.div("!!Email metadata",_class='pbl_roundedGroupLabel')
        fb = top.div(margin_right='15px').formbuilder(cols=1, border_spacing='2px',width='100%',fld_width='100%',tdl_width='8em')
        fb.textbox(value='^.subject', lbl='!!Subject',dropTypes = 'text/plain')
        fb.textbox(value='^.to_address', lbl='!!To',dropTypes = 'text/plain')
        fb.textbox(value='^.from_address', lbl='!!From',dropTypes = 'text/plain')
        fb.textbox(value='^.cc_address', lbl='!!CC',dropTypes = 'text/plain')
        fb.textbox(value='^.bcc_address', lbl='!!BCC',dropTypes = 'text/plain')

        fb.simpleTextArea(value='^.attachments', lbl='!!Attachments',dropTypes = 'text/html')

        editorConstrain = editorConstrain or dict()
        constrain_height = editorConstrain.pop('constrain_height',False)
        constrain_width = editorConstrain.pop('constrain_width',False)
        bc.dataController("""SET .editor.height = letterhead_center_height?letterhead_center_height+'mm': constrain_height;
                             SET .editor.width = letterhead_center_width?letterhead_center_width+'mm':constrain_width;
            """,constrain_height=constrain_height,
                constrain_width=constrain_width,
                letterhead_center_height='^.preview.letterhead_record.center_height',
                letterhead_center_width='^.preview.letterhead_record.center_width',
                _init=True)
        bc.contentPane(region='center',overflow='hidden').ckEditor(value='^.data.content',constrain_height='^.editor.height',
                                                 constrain_width='^.editor.width',**editorConstrain)
                            
    def _te_framePreview(self,frame,table=None):
        bar = frame.top.slotToolbar('5,parentStackButtons,10,fb,*',parentStackButtons_font_size='8pt')                   
        fb = bar.fb.formbuilder(cols=2, border_spacing='0px',margin_top='2px')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.preview.letterhead_id',
                    selected_name='.preview.html_template_name',lbl='!!Letterhead',
                    width='10em', hasDownArrow=True)
        fb.dbSelect(dbtable=table, value='^.preview.selected_id',lbl='!!Record', width='12em',lbl_width='6em',excludeDraft=False)
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
        r.cell('code', name='!!Code', width='10em',edit=True)
        r.cell('description', name='!!Description', width='40em',edit=True)
        r.cell('fieldtype', name='!!Fieldtype', width='10em',edit=dict(values='!!T:Text,L:Integer,D:Date,N:Decimal,B:Boolean,TL:Long Text',tag='filteringSelect'))
        r.cell('format', name='!!Format', width='10em',edit=True)
        r.cell('mask', name='!!Mask', width='15em',edit=True)
        r.cell('values', name='!!Values', width='100%',edit=True)   

class PaletteTemplateEditor(TemplateEditor):
    @struct_method
    def te_paletteTemplateEditor(self,pane,paletteCode=None,maintable=None,**kwargs):
        palette = pane.palettePane(paletteCode=paletteCode or 'template_manager',
                                    title='^.caption',palette_overflow='hidden',
                                    width='750px',height='500px',maxable=True,overflow='hidden',**kwargs)
        palette.remote(self.remoteTemplateEditor,maintable=maintable)

    @public_method
    def remoteTemplateEditor(self,palette,maintable=None):
        sc = palette.templateEditor(maintable=maintable)
        infobar = sc.info.top.bar
        infobar.replaceSlots('#','#,menutemplates,deltpl,savetpl,5')
        infobar.deltpl.slotButton('!!Delete current',iconClass='iconbox trash',
                                action='FIRE .deleteCurrent',disabled='^.currentTemplate.pkey?=!#v')
        infobar.dataController('SET .currentTemplate.path="__newtpl__";',_onBuilt=True)
        infobar.dataFormula(".palette_caption", "prefix+caption",caption="^.caption",prefix='!!Edit ')
        infobar.menutemplates.div(_class='iconbox folder').menu(modifiers='*',storepath='.menu',
                action="""SET .currentTemplate.pkey=$1.pkey;
                          SET .currentTemplate.mode = $1.tplmode;
                          SET .currentTemplate.path = $1.fullpath;""",_class='smallmenu')
        infobar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate = genro.dom.getEventModifiers(event);',
                                disabled='^.data.content?=!#v')
        
        editbar = sc.edit.top.bar
        editbar.replaceSlots('#','#,savetpl,5')
        editbar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate = genro.dom.getEventModifiers(event);',
                                disabled='^.data.content?=!#v')
        
        previewbar = sc.preview.top.bar
        previewbar.replaceSlots('#','#,savetpl,5')
        previewbar.savetpl.slotButton('!!Save template',iconClass='iconbox save',
                                action="""FIRE .savetemplate = genro.dom.getEventModifiers(event);""",
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
        infobar.dataRpc('dummy',self.db.table('adm.userobject').deleteUserObject,pkey='=.currentTemplate.pkey',
                        _onResult='SET .currentTemplate.path="__newtpl__";',_fired='^.deleteCurrent')
        infobar.dataController("""
            if(genro.isDeveloper && modifiers=='Shift'){
                FIRE .savetemplateAsResource;
                return;
            }
            if(currentTemplatePkey){
                FIRE .save_userobject = currentTemplatePkey;
            }else{
                FIRE .save_userobject = '*newrecord*';
            }
        """,modifiers='^.savetemplate',currentTemplateMode='=.currentTemplate.tplmode',
                            currentTemplatePath='=.currentTemplate.path',
                            currentTemplatePkey='=.currentTemplate.pkey',
                            data='=.data')

        infobar.dataController("""
            var template_address;
            genro.dlg.prompt('Save as resource',{lbl:'Tplname',action:function(result){
                    template_address =  table+':'+result;
                    genro.serverCall("saveTemplate",{template_address:template_address,data:data},null,null,'POST');
                }})
        """,_fired='^.savetemplateAsResource',data='=.data',table=maintable)


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
        from_userobject = self.db.table('adm.userobject').userObjectMenu(table,'template') #todo
        for n in from_userobject:
            result.setItem(n.label,None,tplmode='userobject',**n.attr)
        result.setItem('__newtpl__',None,caption='!!New Template')
        return result

    @public_method
    def te_saveTemplate(self,pkey=None,data=None,tplmode=None,table=None,metadata=None,**kwargs):
        record = None
        if data['metadata.email']:
            data['metadata.email_compiled'] = self.te_compileBagForm(table=table,sourcebag=data['metadata.email'],
                                                                    varsbag=data['varsbag'],parametersbag=data['parameters'])
        data['compiled'] = self.te_compileTemplate(table=table,datacontent=data['content'],varsbag=data['varsbag'],parametersbag=data['parameters'])['compiled']
        pkey,record = self.db.table('adm.userobject').saveUserObject(table=table,metadata=metadata,data=data,objtype='template')
        record.pop('data')
        return record
        
class ChunkEditor(PaletteTemplateEditor):
    @public_method
    def te_chunkEditorPane(self,pane,table=None,resource_mode=None,paletteId=None,
                            datasourcepath=None,showLetterhead=False,editorConstrain=None,**kwargs):
        sc = self._te_mainstack(pane,table=table)
        self._te_frameChunkInfo(sc.framePane(title='!!Metadata',pageName='info',childname='info'),table=table,datasourcepath=datasourcepath)
        bar = sc.info.top.bar
        bar.replaceSlots('#','#,customres,menutemplates,savetpl,5')
        bar.menutemplates.div(_class='iconbox folder',tip='!!Copy From').menu(modifiers='*',storepath='.menu',
                action="""var that = this;
                          genro.serverCall('_table.adm.userobject.loadUserObject',{table:'%s',pkey:$1.pkey},function(result){
                                that.setRelativeData('.data',result._value.deepCopy());
                         },null,'POST');
        """ %table,_class='smallmenu')
        bar.dataRemote('.menu',self.te_menuTemplates,table=table,cacheTime=5)

        if resource_mode:
            bar.customres.checkbox(value='^.data.metadata.custom',label='!!Custom')
        else:
            bar.customres.div()
        self._te_saveButton(bar.savetpl,table,paletteId)
        frameEdit = sc.framePane(title='!!Edit',pageName='edit',childname='edit')
        self._te_frameEdit(frameEdit,editorConstrain=editorConstrain)
        if showLetterhead:
            bar = frameEdit.top.bar.replaceSlots('parentStackButtons','parentStackButtons,letterhead_selector')
            fb = bar.letterhead_selector.formbuilder(cols=1,border_spacing='1px')
            if isinstance(showLetterhead,basestring):
                fb.data('.preview.letterhead_id',showLetterhead)
            fb.dbSelect(dbtable='adm.htmltemplate', value='^.preview.letterhead_id',
                        lbl='!!Letterhead',width='15em', hasDownArrow=True)
            fb.dataRecord('.preview.letterhead_record','adm.htmltemplate',pkey='^.preview.letterhead_id',_if='pkey')

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
        bc = frame.center.borderContainer()
        self._te_info_vars(bc,table=table,region='center',
                            fieldsTree_currRecordPath=datasourcepath,
                            fieldsTree_explorerPath='#ANCHOR.dbexplorer')
        #self._te_info_parameters(bc,region='center')
    
    def _te_framePreviewChunk(self,frame,table=None,datasourcepath=None):
        bar = frame.top.slotToolbar('5,parentStackButtons,10,fb,*',parentStackButtons_font_size='8pt')                   
        fb = bar.fb.formbuilder(cols=1, border_spacing='0px',margin_top='2px')
        if not datasourcepath:
            fb.dbSelect(dbtable=table, value='^.preview.id',lbl='!!Record',width='15em', hasDownArrow=True)
            preview_id = '.preview.id'
        else:
            preview_id = '%s.%s' %(datasourcepath,self.db.table(table).pkey)
        record_id = '^%s' %preview_id
        frame.dataRpc('.preview.renderedtemplate', self.te_getPreview,
                   _POST =True,record_id=record_id,_status='=.status',_if='compiled && _status=="preview"',_else='return new gnr.GnrBag()',
                   compiled='^.data.compiled',template_id='^.preview.letterhead_id')
        frame.center.contentPane(margin='5px').div('^.preview.renderedtemplate')

        
        
    def _te_saveButton(self,pane,table,paletteId):
        pane.slotButton('!!Save',action="""var result = genro.serverCall('te_compileTemplate',{table:table,datacontent:dc,varsbag:vb,parametersbag:pb},null,null,'POST');
                                    data.setItem('compiled',result.getItem('compiled'));
                                    genro.nodeById(paletteId).publish("savechunk");""",
                            iconClass='iconbox save',paletteId=paletteId,table=table,dc='=.data.content',
                            vb='=.data.varsbag',pb='=.data.parametersbag',data='=.data')
        
    
        
