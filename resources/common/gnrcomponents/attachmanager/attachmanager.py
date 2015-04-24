# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrstring import slugify
import os


class AttachManagerViewBase(BaseComponent):

    def th_hiddencolumns(self):
        return '$fileurl'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',counter=True,hidden=True)
        r.fieldcell('description',edit=True,width='20em')
    
    def th_order(self):
        return '_row_count'

class AttachManagerView(AttachManagerViewBase):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',counter=True,hidden=True)
        #tbl.column('filepath' ,name_long='!!Filepath')
        r.fieldcell('description',edit=True,width='20em')
        #r.fieldcell('mimetype')
        r.fieldcell('fileurl',hidden=True)
        r.cell('imp',calculated=True,name='!!Imp.',format_isbutton=True,format_buttonclass='iconbox document',
                format_onclick="""
                    genro.serverCall('_table.'+this.attr.table+'.atc_importAttachment',{pkey:this.widget.rowIdByIndex($1.rowIndex)},
                                     function(){console.log("ocr done")});
                """,width='22px')




class Form(BaseComponent):
    def th_form(self, form):
        sc = form.center.stackContainer(datapath='.record')
        sc.contentPane(overflow='hidden').iframe(src='^.fileurl',_virtual_column='fileurl',height='100%',
                                                width='100%',border='0px',documentClasses=True)
        da = sc.contentPane().div(position='absolute',top='10px',left='10px',right='10px',bottom='10px',
            text_align='center',border='3px dotted #999',rounded=8)

        da.table(height='100%',width='100%').tr().td().div('!!Drop Area',width='100%',
                                                            font_size='30px',color='#999')
        da.div(position='absolute',top=0,bottom=0,left=0,right=0,z_index=10,
            dropTarget=True,dropTypes='Files',
                onDrop="""
                            var form = this.form;
                            form.waitingStatus(true)
                            AttachManager.onDropFiles(this,files,function(){
                                    form.waitingStatus(false);
                                });""",
                _uploader_fkey='=#FORM.record.maintable_id',
                _uploader_onUploadingMethod=self.onUploadingAttachment
            )

        form.dataController("sc.switchPage(newrecord?1:0)",newrecord='^#FORM.controller.is_newrecord',sc=sc.js_widget)

    def th_options(self):
        return dict(showtoolbar=False,showfooter=False)

class ViewPalette(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description',width='100%',name='!!Attachment')
        r.fieldcell('fileurl',hidden=True)

    def th_view(self,view):
        view.top.popNode('bar')

class FormPalette(Form):
    pass

class AttachManager(BaseComponent):
    js_requires='gnrcomponents/attachmanager/attachmanager'

    @struct_method
    def at_attachmentGrid(self,pane,title=None,searchOn=False,pbl_classes=True,datapath='.attachments',screenshot=False,**kwargs):
        bc = pane.borderContainer()

        th = bc.contentPane(region='left',width='400px',splitter=True).inlineTableHandler(relation='@atc_attachments',
                                        viewResource='gnrcomponents/attachmanager/attachmanager:AttachManagerView',
                                        hider=True,autoSave=True,statusColumn=True,
                                        addrow=False,pbl_classes=pbl_classes,
                                        autoSelect=True,

                                     semaphore=False, searchOn=False,datapath=datapath,**kwargs)
        th.view.grid.attributes.update(dropTarget_grid='Files',onDrop='AttachManager.onDropFiles(this,files);',
                                        dropTypes='Files',_uploader_fkey='=#FORM.pkey',
                                        _uploader_onUploadingMethod=self.onUploadingAttachment)
        if screenshot:
            th.view.top.bar.replaceSlots('delrow','delrow,screenshot,5')
            

        readerpane = bc.contentPane(region='center',datapath=datapath,margin='2px',border='1px solid silver')
        readerpane.dataController('SET .reader_url=fileurl',fileurl='^.view.grid.selectedId?fileurl')
        readerpane.iframe(src='^.reader_url',height='100%',width='100%',border=0,documentClasses=True)
        return th

    @struct_method
    def at_slotbar_screenshot(self,pane,**kwargs):
        pane.slotButton('"Snapshot',iconClass='iconbox photo',action="""FIRE .takeSnapshot;""")
        pane.dataController("""
                        var attachment_table = this.getInheritedAttributes()['table'];
                        var kw = {attachment_table:attachment_table,maintable_id:fkey,onUploadingMethod:onUploadingMethod,uploaderId:'attachmentManager'};
                        var fm = genro.getParentGenro().framedIndexManager;
                        if(fm){
                            fm.callOnCurrentIframe('dev','takePicture',[kw]);
                        }else{
                            genro.dev.takePicture(kw);
                        }
            """,_fired='^.takeSnapshot',fkey='=#FORM.pkey',onUploadingMethod=self.onUploadingAttachment)


    @struct_method
    def at_attachmentPane(self,pane,title=None,searchOn=False,pbl_classes=True,
                        datapath='.attachments',mode=None,viewResource=None,**kwargs):
        frame = pane.framePane(frameCode='attachmentPane_#')
        bc = frame.center.borderContainer()
        mode = mode or 'sidebar'
        d = dict(sidebar=dict(region='left',width='400px'),headline=dict(region='top',height='300px'))
        th = bc.contentPane(splitter=True,childname='atcgrid',**d[mode]).inlineTableHandler(relation='@atc_attachments',
                                        viewResource= viewResource or 'gnrcomponents/attachmanager/attachmanager:AttachManagerView',
                                        hider=True,autoSave=True,statusColumn=True,
                                        addrow=False,delrow=False,pbl_classes=pbl_classes,
                                        autoSelect=True,
                                     semaphore=False, searchOn=False,datapath=datapath,**kwargs)
        th.view.top.popNode('bar')
        th.view.grid.attributes.update(dropTarget_grid='Files',onDrop='AttachManager.onDropFiles(this,files);',
                                        dropTypes='Files',_uploader_fkey='=#FORM.pkey',
                                        _uploader_onUploadingMethod=self.onUploadingAttachment)


        readerpane = bc.contentPane(region='center',datapath=datapath,margin='2px',border='1px solid #efefef',rounded=6,childname='atcviewer',overflow='hidden')
        readerpane.iframe(src='^.reader_url',height='100%',width='100%',border=0,documentClasses=True)
        readerpane.dataController('SET .reader_url=fileurl',fileurl='^.view.grid.selectedId?fileurl')
        bar = frame.top.slotToolbar('5,vtitle,*,delrowbtn',vtitle=title or '!!Attachments')
        bar.delrowbtn.slotButton('!!Delete attachment',iconClass='iconbox delete_row',action='gr.publish("delrow")',gr=th.view.grid)
        return frame

    @struct_method
    def at_attachmentMultiButtonFrame(self,pane,datapath='.attachments',**kwargs):
        frame = pane.multiButtonForm(frameCode='attachmentPane_#',datapath=datapath,
                            relation='@atc_attachments',
                            caption='description',
                            formResource='gnrcomponents/attachmanager/attachmanager:Form',
                            multibutton_deleteAction="""
                                var s = this._value.getNode('store').gnrwdg.store;
                                s.deleteAsk([value]);
                            """,
                            multibutton_deleteSelectedOnly=True,
                            store_order_by='$_row_count')
        frame.multiButtonView.item(code='add_atc',caption='+',frm=frame.form.js_form,
                                    action='frm.newrecord();',
                parentForm=True,deleteAction=False,disabled='==!_store || _store.len()==0 || _flock',
                _store='^.store',_flock='^#FORM.controller.locked')
        table = frame.multiButtonView.itemsStore.attributes['table']
        bar = frame.top.bar.replaceSlots('mbslot','mbslot,15,changeName')
        fb = bar.changeName.div(_class='iconbox tag',hidden='^.form.controller.is_newrecord',tip='!!Change description').tooltipPane(
                connect_onClose='FIRE .saveDescription;',
            ).div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.form.record.description',lbl='!!Description')
        frame.dataController("""
            if(frm.getParentForm().isNewRecord()){
                frame.setHiderLayer(true);
            }else{
                frame.setHiderLayer(false);
                frm.newrecord();
            }
            """,store='^.store',_delay=100,
            _if='!store || store.len()==0',frm=frame.form.js_form,frame=frame)
        frame.dataController("frm.lazySave()",frm=frame.form.js_form,_fired='^.saveDescription')
        frame.onDbChanges(action="""
            var that = this;
            if(_node.attr.from_page_id!=genro.page_id){
                return;
            }   
            dbChanges.forEach(function(c){
                if(c.dbevent=='I'){
                    frm.goToRecord(c.pkey);
                }else if(c.dbevent=='D'){
                    console.log('deleted',c.pkey);
                }
            })
            """,table=table,frm=frame.form.js_form,_delay=1,store='=.store')

    @public_method
    def onUploadingAttachment(self,kwargs):
        attachment_table = kwargs.get('attachment_table')
        maintable = attachment_table[0:-4]
        maintable_id = kwargs.get('maintable_id')
        maintableobj = self.db.table(maintable)
        filename = kwargs.get('filename')
        description,ext = os.path.splitext(filename)
        description = slugify(description)
        filename = '%s%s' %(description,ext)
        kwargs['filename'] = filename
        path = os.path.join(maintable.replace('.','_'),maintable_id)
        if hasattr(maintableobj,'atc_getAttachmentPath'):
            path = maintableobj.atc_getAttachmentPath(pkey=maintable_id)
        kwargs['uploadPath'] = 'vol:%s' %path
        record = dict(maintable_id=maintable_id,mimetype=kwargs.get('mimetype'),description=description,filepath=os.path.join(path,filename))
        self.db.table(attachment_table).insert(record)
        self.db.commit()
