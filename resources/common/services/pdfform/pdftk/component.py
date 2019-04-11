# -*- coding: utf-8 -*-

# pysftp component
# Created by Francesco Porcari on 2017-12-18.
# Copyright (c) 2017 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import slugify
from time import time


class PdfTkEditor(BaseComponent):
    py_requires = 'gnrcomponents/framegrid:FrameGrid'

    @struct_method
    def pdftk_pdfTkEditor(self,parent,pdfFile=None,storepath=None,table=None,nodeId=None,**kwargs):
        nodeId = nodeId or 'pdfTkEditor'
        bc = parent.borderContainer(nodeId=nodeId,_workspace=True,_anchor=True,**kwargs)
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2)
        fb.dataRpc('#WORKSPACE.pdfFilesBag',self.pdftk_getFiles,table=table,
                    _onBuilt=True,_fired='^#WORKSPACE.reloadFilesBag')
        fb.dataRpc(storepath,self.pdftk_getFields, data='=%s' %storepath,
            pdfFile=pdfFile)
        fb.filteringSelect(value=pdfFile,
                            storepath='#WORKSPACE.pdfFilesBag',
                            lbl='Pdf form',storeid='fullpath')
        fb.dropUploader(nodeId='%s_uploader' %nodeId, label= 'Upload pdf form',
                        uploadPath='pdf_forms:%s' %table.replace('.','/'),
                        onResult='FIRE #WORKSPACE.reloadFilesBag',font_size='9pt')
        fb.dataFormula('#WORKSPACE.pdfViewerUrl','pdfFile?"/"+pdfFile:null',pdfFile=pdfFile)
        fb.dataFormula('#WORKSPACE.viewerUrl',"previewUrl || pdfViewerUrl",
                        pdfViewerUrl='^#WORKSPACE.pdfViewerUrl',
                        previewUrl='^#WORKSPACE.previewUrl')
        fb.dataRpc('#WORKSPACE.previewUrl',self.pdftk_previewMake,
                        record_id='^test_record_id',
                        tbl=table,
                        pdfFields='=%s' %storepath,
                        pdfFile=pdfFile,
                        _fired='^#WORKSPACE.updatePreview')
        center = bc.borderContainer(region='center')
        self.pdftk_viewer(center.framePane(region='center', margin_left='4px',margin='2px',
                            border='1px solid #efefef',rounded=4),table=table)
        self.pdftk_fields(center.contentPane(region='left', width='400px', splitter=True), storepath=storepath,table=table)


    def pdftk_viewer(self,frame,table=None):
        bar = frame.top.slotToolbar('2,fbrec,*,2')
        fb = bar.fbrec.formbuilder(border_spacing='1px')
        fb.dbselect(value='^test_record_id',lbl='Test Record',dbtable=table)
        pane = frame.center.contentPane(overflow='hidden')
        pane.iframe(src='^#WORKSPACE.viewerUrl',height='100%',
                                        width='100%',border=0)

    def pdftk_fields(self,pane, storepath=None,table=None):
        frame = pane.bagGrid(datapath='#WORKSPACE.pdfFields',
                                struct=self.struct_fields,
                                pbl_classes=True,margin='2px',
                                storepath=('#ANCHOR%s' %storepath) if storepath.startswith('.') else storepath,
                                datamode='bag',
                                addrow=False,delrow=False)

        frame.left.slotBar('5,fieldsTree,*',
                            fieldsTree_table=table,
                            fieldsTree_dragCode='fieldvars',
                            border_right='1px solid silver',
                            closable=True,width='150px',
                            fieldsTree_height='100%',splitter=True)
        grid = frame.grid
        grid.data('.table',table)
        grid.dragAndDrop(dropCodes='fieldvars:row')
        grid.dataController("""grid.gridEditor.setCellValue(droppedInfo.row,'field_path',data.fieldpath);""",
                            data="^.dropped_fieldvars",droppedInfo='=.droppedInfo_fieldvars',
                            grid=grid.js_widget)

    def struct_fields(self, struct):
        r=struct.view().rows()
        r.cell('pdf_field', name='Campo Form',width='10em')
        r.cell('field_path', name='Valore',width='100%', edit=True)

    @public_method
    def pdftk_previewMake(self,record_id=None,pdfFile=None,
                            pdfFields=None,tbl=None,**kwargs):
        if not (record_id and pdfFields and pdfFile):
            return
        pdfform_service = self.site.getService('pdfform')
        output = self.site.storageNode('page:temp_template_%s.pdf'%record_id)
        pdfform_service.fillFromRecord(pdfFields=pdfFields,pdfFile=pdfFile, table=tbl, record_id=record_id, output=output)
        return output.url(nocache='%i'%time())



    @public_method
    def pdftk_getFiles(self,table=None):
        forms = self.site.getService('pdfform').getForms(table=table)
        out_bag = Bag()
        for i,form in enumerate(forms):
            out_bag.addItem('r_%s'%i,None,
                fullpath=form.fullpath, caption=form.cleanbasename,
                url = form.url())
        return out_bag

    @public_method
    def pdftk_getFields(self, pdfFile=None, data=None):
        fields = self.site.getService('pdfform').getFields(template=pdfFile) or []
        out_bag = data or Bag()
        for i,field in enumerate(fields):
            field_key = field.replace('.','_')
            if field_key not in out_bag:
                out_bag[field_key] = Bag(pdf_field=field, field_path=None)
        return out_bag


class PalettePdfFormEditor(PdfTkEditor):
    @struct_method
    def pdftk_pdfFormEditorPalette(self,pane,paletteCode=None,maintable=None,**kwargs):
        palette = pane.palettePane(paletteCode=paletteCode or 'pdfFormE_manager',
                                    title='^.caption',
                                    palette_overflow='hidden',
                                    width='750px',height='500px',
                                    maxable=True,
                                    overflow='hidden',**kwargs)
        palette.remote(self.pdftk_remotePdfFormEditor,maintable=maintable,
                        rootId='%s_editor' %paletteCode)

    @struct_method
    def pdftk_pdfTkEditorUserObject(self,pane,maintable=None,rootId=None):
        frame = pane.framePane()
        frame.top.slotToolbar('2,vtitle,*',vtitle='Editor')
        bc = frame.center.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(cols=3,
                                            border_spacing='4px',fld_width='100%',
                                            datapath='.data.metadata',colswidth='auto')
        fb.textbox(value='^.author',lbl='!!Author',tdf_width='12em')
        fb.numberTextBox(value='^.version',lbl='!!Version',width='4em')
        fb.dateTextBox(value='^.date',lbl='!!Date',width='6em')
        bc.pdfTkEditor(region='center',pdfFile='^.data.pdfFile',
                        storepath='.data.pdfFields',
                        table=maintable,
                        nodeId=rootId)
        return frame

    @public_method
    def pdftk_remotePdfFormEditor(self,palette,maintable=None,rootId=None):
        frame = palette.pdfTkEditorUserObject(maintable=maintable, rootId=rootId)
        infobar = frame.top.bar
        infobar.replaceSlots('#','#,menutemplates,deltpl,savepdfform,5')
        infobar.deltpl.slotButton('!!Delete current',iconClass='iconbox trash',
                                action='FIRE .deleteCurrent',disabled='^.currentPdfForm.pkey?=!#v')
        infobar.dataController('SET .currentPdfForm.path="__newtpl__";',_onBuilt=True)
        infobar.dataFormula(".palette_caption", "prefix+caption",caption="^.caption",prefix='!!Edit ')
        infobar.menutemplates.div(_class='iconbox folder').menu(modifiers='*',storepath='.menu',
                action="""SET .currentPdfForm.pkey=$1.pkey;
                          SET .currentPdfForm.mode = $1.tplmode;
                          SET .currentPdfForm.path = $1.fullpath;""",_class='smallmenu')
        infobar.savepdfform.slotButton('!!Save PDF form',iconClass='iconbox save',
                    action='FIRE .savetemplate = genro.dom.getEventModifiers(event);')

        #editbar = sc.edit.top.bar
        #editbar.replaceSlots('#','#,savetpl,5')
        #editbar.savetpl.slotButton('!!Save template',iconClass='iconbox save',action='FIRE .savetemplate = genro.dom.getEventModifiers(event);',
        #                        disabled='^.data.content?=!#v')

        #previewbar = sc.preview.top.bar
        #previewbar.replaceSlots('#','#,savetpl,5')
        #previewbar.savetpl.slotButton('!!Save template',iconClass='iconbox save',
        #                        action="""FIRE .savetemplate = genro.dom.getEventModifiers(event);""",
        #                        disabled='^.data.content?=!#v')


        infobar.dataController("""
            var editorbag = this.getRelativeData();
            if(tplpath=='__newtpl__'){
                editorbag.setItem('data',new gnr.GnrBag());
                editorbag.setItem('data.metadata.author',user);
                editorbag.setItem('userobject_meta',new gnr.GnrBag());
                editorbag.setItem('userobject_meta.flags', 'is_print');
                editorbag.setItem('caption',newcaption);
            }else if(pkey){

                genro.serverCall('_table.adm.userobject.loadUserObject',{table:table,pkey:pkey},function(result){
                    editorbag.setItem('data',result._value.deepCopy());
                    editorbag.setItem('mode','userobject');
                    editorbag.setItem('caption',result.attr.description || result.attr.code);
                    editorbag.setItem('userobject_meta',new gnr.GnrBag(result.attr));
                },null,'POST')
            }
        """,tplpath="^.currentPdfForm.path",tplmode='=.currentPdfForm.tplmode',
                pkey='=.currentPdfForm.pkey',
                table=maintable,newcaption='!!New PDF form',
                user=self.user)
        infobar.dataRpc('dummy',self.db.table('adm.userobject').deleteUserObject,pkey='=.currentPdfForm.pkey',
                        _onResult='SET .currentPdfForm.path="__newtpl__";',_fired='^.deleteCurrent')
        infobar.dataController("""
            if(currentPdfFormPkey){
                FIRE .save_userobject = currentPdfFormPkey;
            }else{
                FIRE .save_userobject = '*newrecord*';
            }
        """,modifiers='^.savetemplate',currentPdfFormMode='=.currentPdfForm.tplmode',
                            currentPdfFormPath='=.currentPdfForm.path',
                            currentPdfFormPkey='=.currentPdfForm.pkey',
                            data='=.data')

        infobar.dataController("""
                var that = this;
                var savepath = this.absDatapath('.userobject_meta');
                var kw = {'tplmode':'userobject','table':table,
                        'data':data,metadata:'='+savepath}
                genro.dev.userObjectDialog(_T('Save Pdf form'),savepath,
                function(dialog) {
                    genro.serverCall(handler,kw,
                        function(result) {
                            that.setRelativeData('.currentPdfForm.pkey',result['id']);
                            that.setRelativeData('.currentPdfForm.path',result['code']);
                            dialog.close_action();
                        },null,'POST');
            });
            """,pkey='^.save_userobject',data='=.data',table=maintable,handler=self.pdftk_savePdfForm)
        infobar.dataRemote('.menu',self.pdftk_pdftkUoMenu,table=maintable,cacheTime=5)

    @public_method
    def pdftk_pdftkUoMenu(self,table=None):
        result = Bag()
        from_userobject = self.db.table('adm.userobject').userObjectMenu(table,'pdfform') #todo
        for n in from_userobject:
            result.setItem(n.label,None,tplmode='userobject',**n.attr)
        result.setItem('__newtpl__',None,caption='!!New pdf form')
        return result

    @public_method
    def pdftk_savePdfForm(self,pkey=None,data=None,tplmode=None,table=None,metadata=None,**kwargs):
        pkey,record = self.db.table('adm.userobject').saveUserObject(table=table,metadata=metadata,data=data,objtype='pdfform')
        record.pop('data')
        return record



