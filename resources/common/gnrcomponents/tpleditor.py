# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
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
    def te_getPreview(self, record_id=None, compiled=None, templates=None,**kwargs):
        tplbuilder = self.getTemplateBuilder(compiled=compiled, templates=templates)
        return self.renderTemplate(tplbuilder, record_id=record_id, extraData=Bag(dict(host=self.request.host)))

    
    def getTemplateBuilder(self, compiled=None, templates=None):
        htmlbuilder = BagToHtml(templates=templates, templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        htmlbuilder.doctemplate = compiled
        htmlbuilder.virtual_columns = compiled.getItem('main?virtual_columns')
        htmlbuilder.locale = compiled.getItem('main?locale')
        htmlbuilder.formats = compiled.getItem('main?formats')
        htmlbuilder.data_tblobj = self.db.table(compiled.getItem('main?maintable'))
        return htmlbuilder
        
    def renderTemplate(self, templateBuilder, record_id=None, extraData=None, locale=None, formats=None,**kwargs):
        record = Bag()
        if record_id:
            record = templateBuilder.data_tblobj.record(pkey=record_id,
                                                        virtual_columns=templateBuilder.virtual_columns).output('bag')
        if extraData:
            record.update(extraData)
        locale = locale or templateBuilder.locale
        formats = templateBuilder.formats or dict()
        formats.update(templateBuilder.formats or dict())
        record.setItem('_env_', Bag(self.db.currentEnv))
        #record.setItem('_template_', templateBuilder.doctemplate_info)
        body = templateBuilder(htmlContent=templateReplace(templateBuilder.doctemplate,record, safeMode=True,noneIsBlank=False,locale=locale, formats=formats),
                            record=record,**kwargs)
        return body
    @public_method
    def te_compileTemplate(self,table=None,datacontent=None,varsbag=None,record_id=None,templates=None):
        tplvars =  varsbag.digest('#v.varname,#v.fieldpath,#v.virtual_column,#v.format')
        result = Bag()
        formats = dict()
        columns = []
        virtual_columns = []
        varsdict = dict()
        for varname,fldpath,virtualcol,format in tplvars:
            varsdict[varname] = '$%s' %fldpath
            formats[fldpath] = format
            columns.append(fldpath)
            if virtualcol:
                virtual_columns.append(fldpath)
                
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
                            columns=','.join(columns),formats=formats)
        result.setItem('compiled',compiled)
        if record_id:
            result.setItem('preview',self.te_getPreview(compiled=compiled,record_id=record_id,templates=templates))
        return result

class TemplateEditor(TemplateEditorBase):
    py_requires='foundation/macrowidgets:RichTextEditor,gnrcomponents/framegrid:FrameGrid'
    css_requires='public'
    @struct_method
    def te_templateEditor(self,pane,storepath=None,maintable=None,**kwargs):
        sc = pane.stackContainer(datapath='.template_editor',selectedPage='^.status',_fakeform=True)
        sc.dataRpc('dummy',self.te_compileTemplate,varsbag='=.data.varsbag',
                    datacontent='=.data.content',table=maintable,_if='_status=="preview"&&datacontent&&varsbag',
                    _status='^.status',record_id='=.preview.selected_id',templates='=.preview.html_template_name',
                    _onResult="""
                    SET .data.compiled = result.getItem('compiled').deepCopy();
                    SET .preview.renderedtemplate = result.getItem('preview');
                    """)
        self._te_frameInfo(sc.framePane(title='!!Metadata',pageName='info',childname='info'),table=maintable)
        self._te_frameEdit(sc.framePane(title='!!Edit',pageName='edit',childname='edit'),table=maintable)
        self._te_framePreview(sc.framePane(title='!!Preview',pageName='preview',childname='preview'),table=maintable)
        return sc

    def _te_frameInfo(self,frame,table=None):
        frame.top.slotToolbar('5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        bc = frame.center.borderContainer()
        top = bc.borderContainer(region='top',height='24ex')
        center = bc.borderContainer(region='center')
        top_top = top.contentPane(region='top')
        #top_top.div('!!Template Info',_class='pbl_roundedGroupLabel')
        fb = top_top.div(margin='5px').formbuilder(cols=5, border_spacing='4px',fld_width='100%',width='100%',
                                                tdl_width='6em',datapath='.data.metadata')
        fb.textbox(value='^.author',lbl='!!Author',width='15em')
        fb.numberTextBox(value='^.version',lbl='!!Version')
        fb.dateTextBox(value='^.date',lbl='!!Date')
        fb.checkbox(value='^.is_print',label='!!Print')
        fb.checkbox(value='^.is_mail',label='!!Mail')
        fb.dataController("""var result = [];
                             if(is_mail){result.push('is_mail');}
                             if(is_print){result.push('is_print');}
                             SET #FORM.userobject_meta.flags = result.join(',');""",
                        is_mail="^.is_mail",is_print='^.is_print')
        fb.textbox(value='^.summary',lbl='!!Summary',colspan=5)
        parsframe = top.frameGrid(region='center',
                                datamode='bag',datapath='.parametersgrid',
                                storepath='#FORM.data.parameters', 
                                struct=self._te_metadata_struct,selfDragRows=True)
        parsframe.top.slotToolbar('gridtitle,*,addrow,delrow',gridtitle='!!Parameters')
        gridEditor = parsframe.grid.gridEditor()
        gridEditor.textbox(gridcell='code')
        gridEditor.textbox(gridcell='description')
        gridEditor.filteringSelect(gridcell='fieldtype',values='!!T:Text,L:Integer,D:Date,N:Decimal,B:Boolean,TL:Long Text')
        gridEditor.textbox(gridcell='values')        
        gridEditor.filteringSelect(gridcell="mandatory",values="!!F:No,T:Yes")
                
        frametree= center.framePane(region='left',margin='2px',margin_bottom='4px',_class='pbl_roundedGroup',width='35em')
        frametree.fieldsTree(table=table,trash=False)        
        frametree.top.div('!!Fields',_class='pbl_roundedGroupLabel')  
        def struct(struct):
            r = struct.view().rows()
            r.cell('fieldname', name='Field', width='100%')
            r.cell('varname', name='As', width='6em')
            r.cell('format', name='Format', width='6em')

        varsframe = center.frameGrid(margin='2px',region='center',
                                    datapath='.varsgrid',
                                    storepath='#FORM.data.varsbag',
                                    struct=struct,datamode='bag',
                                    _class='pbl_roundedGroup')
        tablecode = table.replace('.','_')
        dropCode = 'gnrdbfld_%s' %tablecode
        editor = varsframe.grid.gridEditor()
        editor.textbox(gridcell='varname')
        editor.textbox(gridcell='format')
        varsframe.top.slotBar(slots='gridtitle,*,delrow',gridtitle='!!Variables',_class='slotbar_toolbar pbl_roundedGroupLabel')
        varsframe.grid.dragAndDrop(dropCodes=dropCode)
        varsframe.grid.dataController("""var caption = data.fullcaption;
                                var varname = caption.replace(/\W/g,'_').toLowerCase()
                                grid.addBagRow('#id', '*', grid.newBagRow({'fieldpath':data.fieldpath,fieldname:caption,varname:varname,virtual_column:data.virtual_column}));""",
                             data="^.dropped_%s" %dropCode,grid=varsframe.grid.js_widget)        
      

    
    def _te_frameEdit(self,frame,table=None):
        frame.top.slotToolbar(slots='5,parentStackButtons,*',parentStackButtons_font_size='8pt')
        self.RichTextEditor(frame.center.contentPane(), value='^.data.content',
                            toolbar='simple')
                            
    def _te_framePreview(self,frame,table=None):
        frame.dataRpc('.preview.pkeys', self.te_getPreviewPkeys,
                   maintable=table,_POST =True,
                   _onResult="""
                                 var first_row = result[0];
                                 SET .preview.selected_id = first_row; 
                                 SET .preview.idx=0;
                                """
                   )
        bar = frame.top.slotToolbar('5,parentStackButtons,10,fb,*,prev,next',parentStackButtons_font_size='8pt')                   
        fb = bar.fb.formbuilder(cols=2, border_spacing='0px',margin_top='2px')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.preview.html_template_id',
                    selected_name='.preview.html_template_name',lbl='!!Letterhead',
                    width='10em', hasDownArrow=True)
        fb.dbSelect(dbtable=table, value='^.preview.selected_id',lbl='!!Record', width='12em',lbl_width='6em')
                    
        fb.dataRpc('.preview.renderedtemplate', self.te_getPreview,
                   _POST =True,record_id='^.preview.selected_id',
                   templates='^.preview.html_template_name',
                   compiled='=.data.compiled')
        
        bar.prev.slotButton('!!Previous',
                   action='idx = idx>0?idx-1:10; SET .selected_id = pkeys[idx]; SET .idx = idx;',
                   idx='=.preview.idx', pkeys='=.preview.pkeys',
                   iconClass="iconbox previous")
        bar.next.slotButton('!!Next',
                   action='idx = idx<=pkeys.length?idx+1:0; SET .selected_id = pkeys[idx]; SET .idx = idx;'
                   , idx='=.preview.idx', pkeys='=.preview.pkeys',
                   iconClass="iconbox next")
        frame.center.contentPane(margin='5px',background='white',border='1px solid silver',rounded=4,padding='4px').div('^.preview.renderedtemplate')
    
    def _te_metadata_struct(self,struct):
        r = struct.view().rows()
        r.cell('code', name='!!Code', width='5em')
        r.cell('description', name='!!Description', width='100%')
        r.cell('fieldtype', name='!!Fieldtype', width='10em')
        r.cell('values', name='!!Values', width='10em')
        r.cell('mandatory', name='!!Mandatory',width='7em')  
     
    

class PaletteTemplateEditor(TemplateEditor):
    @struct_method
    def te_paletteTemplateEditor(self,pane,paletteCode=None,maintable=None,**kwargs):
        palette = pane.palettePane(paletteCode=paletteCode or '%s_template_manager' %maintable.replace('.','_'),
                                    title='^.template_editor.caption',
                                    width='700px',height='500px',**kwargs)
        sc = palette.templateEditor(maintable=maintable)
        infobar = sc.info.top.bar
        infobar.replaceSlots('#','#,menutemplates,savetpl,5')
        infobar.data('.palette_caption','!!New template')
        infobar.dataFormula(".palette_caption", "prefix+caption",caption="^.caption",prefix='!!Edit ')
        infobar.menutemplates.div(_class='iconbox folder').menu(modifiers='*',storepath='.menu',
                action="""SET .currentTemplate=new gnr.GnrBag({path:$1.fullpath,tplmode:$1.tplmode,pkey:$1.pkey}); SET .caption=$1.caption;""")
        infobar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate',
                                disabled='^.data.content?=!#v')
        infobar.dataController("""
            var editorbag = this.getRelativeData();
            if(tplpath=='__newtpl__'){
                editorbag.setItem('data',new gnr.GnrBag());
                editorbag.setItem('userobject_meta',new gnr.GnrBag());
            }else if (tplmode=='doctemplate'){
                var bag = new gnr.GnrBag();
                genro.serverCall('app.getRecord',{table:'adm.doctemplate',pkey:pkey},
                    function(result){
                        bag.setItem('content',result._value.getItem('content'));
                        bag.setItem('varsbag',result._value.getItem('varsbag'));
                        bag.setItem('compiled',result._value.getItem('templatebag'));
                        editorbag.setItem('data',bag);
                    }
                );
            }else if(tplmode=='userobject'){
                genro.serverCall('th_loadUserObject',{table:table,pkey:pkey},function(result){
                    editorbag.setItem('data',result._value.deepCopy());
                    editorbag.setItem('userobject_meta',new gnr.GnrBag(result.attr));
                })
            }
        """,tplpath="^.currentTemplate.path",tplmode='=.currentTemplate.tplmode',pkey='=.currentTemplate.pkey',table=maintable)
        infobar.dataController("""
            if(currentTemplatePath && currentTemplatePath!='__newtpl__'){
                if(currentTemplateMode!='userobject'){
                    genro.serverCall('te_saveTemplate',{pkey:currentTemplatePkey,data:data,tplmode:currentTemplateMode});
                }else{
                    FIRE .save_userobject = currentTemplatePkey;
                }
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
                            that.setRelativeData('.currentTemplate',new gnr.GnrBag({path:result['code'],pkey:result['id'],mode:"userobject"}));
                            that.setRelativeData('.caption',result['description'] || result['code']);
                            dialog.close_action();
                        });
            });
            """,pkey='^.save_userobject',data='=.data',table=maintable)
        infobar.dataRemote('.menu',self.te_menuTemplates,table=maintable,cacheTime=5)
        
    @public_method
    def te_menuTemplates(self,table=None):
        result = Bag()
        #from_resources = None #todo
        from_userobject = self.th_listUserObject(table,'template') #todo
        from_doctemplate = Bag()
        f = self.db.table('adm.doctemplate').query(where='$maintable=:t',t=table).fetch()
        for r in f:
            from_doctemplate.setItem(r['pkey'],None,caption=r['name'],tplmode='doctemplate',pkey=r['pkey'])
        result.update(from_doctemplate)
        for n in from_userobject:
            result.setItem(n.label,None,tplmode='userobject',caption=n.attr.get('description') or n.attr.get('description'),**n.attr)
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
            varsbag=data['varsbag']
            if varsbag and len(varsbag)>0:
                data['compiled'] = self.te_compileTemplate(table=table,datacontent=data['content'],varsbag=varsbag)
            pkey,record = self.th_saveUserObject(table=table,metadata=metadata,data=data,objtype='template')
            record.pop('data')
        return record
        