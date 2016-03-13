# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrbag import Bag

class FrameGridSlots(BaseComponent):
    @struct_method
    def fgr_slotbar_export(self,pane,_class='iconbox export',mode='xls',enable=None,rawData=True,parameters=None,**kwargs):
        kwargs.setdefault('visible',enable)
        parameters = parameters or dict()
        mode = parameters.get('mode','xls')
        gridattr = pane.frame.grid.attributes
        table = gridattr.get('table')
        placeholder = table.replace('.','_') if table else None
        return pane.slotButton(label='!!Export',publish='serverAction',
                                command='export',opt_export_mode=mode or 'xls',
                                
                                opt_downloadAs=parameters.get('downloadAs'),
                                opt_rawData=rawData, iconClass=_class,
                                opt_localized_data=True,
                                ask=dict(title='Export selection',skipOn='Shift',
                                        fields=[dict(name='opt_downloadAs',lbl='Download as',placeholder=placeholder),
                                                dict(name='opt_export_mode',wdg='filteringSelect',values='xls:Excel,csv:CSV',lbl='Mode'),
                                                dict(name='opt_localized_data',wdg='checkbox',label='Localized data')]),

                                **kwargs) 
       
    @struct_method
    def fgr_slotbar_addrow(self,pane,_class='iconbox add_row',disabled='^.disabledButton',enable=None,delay=300,defaults=None,**kwargs):
        kwargs.setdefault('visible',enable)
        menupath = None
        if defaults:
            menubag = Bag()
            for i,(caption,default_kw) in enumerate(defaults):
                menubag.setItem('r_%i' %i,None,caption=caption,default_kw=default_kw)
            pane.data('.addrow_menu_store',menubag)
            menupath = '.addrow_menu_store'
        return pane.slotButton(label='!!Add',publish='addrow',iconClass=_class,disabled=disabled,
                                _delay=delay,menupath=menupath,**kwargs)
         
    @struct_method
    def fgr_slotbar_delrow(self,pane,_class='iconbox delete_row',enable=None,disabled='^.disabledButton',**kwargs):
        kwargs.setdefault('visible',enable)
        frameCode = kwargs['frameCode']
        pane.dataController("""SET .deleteButtonClass = deleteButtonClass;
                            if(disabled){
                                SET .deleteDisabled = true;
                                return;
                            }
                            var grid = genro.wdgById(frameCode+'_grid');
                            var protectedPkeys = grid.getSelectedProtectedPkeys();
                            if(!protectedPkeys){
                                SET .deleteDisabled = false;
                                return
                            }
                            var store = grid.collectionStore? grid.collectionStore():null;
                            if(!store || !store.allowLogicalDelete){
                                SET .deleteDisabled = true;
                                return
                            }
                            SET .deleteDisabled = false;
                            SET .deleteButtonClass = deleteButtonClass +' _logical_delete';
                          """,
                            disabled=disabled,deleteButtonClass=_class,frameCode=frameCode,_onBuilt=True,
                            **{str('subscribe_%s_grid_onSelectedRow' %frameCode):True})
        pane.data('.deleteButtonClass',_class)
        return pane.slotButton(label='!!Delete',publish='delrow',iconClass='^.deleteButtonClass',disabled='^.deleteDisabled',**kwargs)
    
    @struct_method
    def fgr_slotbar_archive(self,pane,_class='box iconbox',enable=None,disabled='^.disabledButton',parentForm=True,**kwargs):
        button = pane.slotButton(label='!!Archive at date',publish='archive',iconClass=_class,
                        disabled=disabled,parentForm=parentForm,**kwargs)
        return button
        
    @struct_method
    def fgr_slotbar_viewlocker(self, pane,frameCode=None,**kwargs):
       # kw['subscribe_%s_onLockChange' %storeId] = "this.widget.setIconClass($1.locked?'icnBaseLocked':'icnBaseUnlocked');"
        pane.slotButton('!!Locker',publish='viewlocker',iconClass='==_locked?"iconbox lock":"iconbox unlock";',_locked='^.locked',**kwargs)
    
    @struct_method
    def fgr_slotbar_updrow(self,pane,_class='icnBaseEdit',enable=None,parentForm=True,**kwargs):
        kwargs.setdefault('visible',enable)
        return pane.slotButton(label='!!Update',publish='updrow',iconClass=_class,parentForm=parentForm,**kwargs)

    @struct_method
    def fgr_slotbar_gridreload(self,pane,_class='icnFrameRefresh box16',frameCode=None,**kwargs):
        return pane.slotButton(label='!!Reload',publish='reload',iconClass=_class,**kwargs)
    
    @struct_method
    def fgr_slotbar_gridsave(self,pane,**kwargs):
        return pane.slotButton(label='!!Save',publish='saveChangedRows',
                               disabled='==status!="changed"',iconClass="iconbox save",
                                status='^.grid.editor.status',**kwargs)
    @struct_method
    def fgr_slotbar_gridsemaphore(self,pane,**kwargs):
        return pane.div(_class='editGrid_semaphore',padding_left='4px')
                                
class FrameGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGridSlots'
    @extract_kwargs(top=True,grid=True)
    @struct_method
    def fgr_frameGrid(self,pane,frameCode=None,struct=None,storepath=None,dynamicStorepath=None,structpath=None,
                    datamode=None,table=None,grid_kwargs=True,top_kwargs=None,iconSize=16,
                    _newGrid=None,**kwargs):
        pane.attributes.update(overflow='hidden')
        frame = pane.framePane(frameCode=frameCode,center_overflow='hidden',**kwargs)
        grid_kwargs.setdefault('_newGrid',_newGrid)
        grid_kwargs.setdefault('structpath',structpath)
        grid_kwargs.setdefault('sortedBy','^.sorted')
        grid_kwargs['selfsubscribe_addrow'] = grid_kwargs.get('selfsubscribe_addrow','this.widget.addRows($1._counter,$1.evt);')
        grid_kwargs['selfsubscribe_delrow'] = grid_kwargs.get('selfsubscribe_delrow','this.widget.deleteSelectedRows();')
        grid_kwargs['selfsubscribe_archive'] = grid_kwargs.get('selfsubscribe_archive','this.widget.archiveSelectedRows();')

        #grid_kwargs['selfsubscribe_setSortedBy'] = """this.setRelativeData(this.attr.sortedBy,$1);"""
        grid_kwargs.setdefault('selectedId','.selectedId')
        frame.includedView(autoWidth=False,
                          storepath=storepath,datamode=datamode,
                          dynamicStorepath=dynamicStorepath,
                          datapath='.grid',
                          struct=struct,table=table,
                          **grid_kwargs)
        if top_kwargs:
            top_kwargs['slotbar_view'] = frame
            frame.top.slotToolbar(**top_kwargs)
        return frame

    @extract_kwargs(default=True,store=True)
    @struct_method
    def fgr_bagGrid(self,pane,storepath=None,dynamicStorepath=None,
                    title=None,default_kwargs=None,
                    pbl_classes=None,gridEditor=True,
                    addrow=True,delrow=True,slots=None,
                    autoToolbar=True,semaphore=None,
                    datamode=None,
                    store_kwargs=True,parentForm=None,**kwargs):
        if pbl_classes:
            _custclass = kwargs.get('_class','')
            kwargs['_class'] = 'pbl_roundedGroup %s' %_custclass
            if pbl_classes=='*':
                kwargs['_class'] = 'pbl_roundedGroup noheader %s' %_custclass
        if gridEditor:
            kwargs['grid_gridEditorPars'] = dict(default_kwargs=default_kwargs)
        kwargs.setdefault('grid_parentForm',parentForm)
        if storepath and ( storepath.startswith('==') or storepath.startswith('^') ):
            dynamicStorepath = storepath
            storepath = '.dummystore'
        datamode= datamode or 'bag'
        frame = pane.frameGrid(_newGrid=True,datamode= datamode,
                                dynamicStorepath=dynamicStorepath,
                                title=title,
                                **kwargs)
        if autoToolbar:
            default_slots = []
            title = title or ''
            default_slots.append('5,vtitle')
            default_slots.append('*')
            if delrow:
                default_slots.append('delrow')
            if addrow:
                default_slots.append('addrow')
            slots = slots or ','.join(default_slots)
            if pbl_classes:
                bar = frame.top.slotBar(slots,_class='pbl_roundedGroupLabel')
            else:
                bar = frame.top.slotToolbar(slots)
            if title:
                bar.vtitle.div(title,_class='frameGridTitle')
            if semaphore:
                bar.replaceSlots('#','#,gridsemaphore')
        if datamode == 'attr':
            store_kwargs.setdefault('storeType','AttributesBagRows')
        store = frame.grid.bagStore(storepath=storepath,parentForm=parentForm,**store_kwargs)
        frame.store = store
        return frame

    @public_method
    def remoteRowControllerBatch(self,handlerName=None,rows=None,**kwargs):
        handler = self.getPublicMethod('rpc',handlerName)
        result = Bag()
        if not handler:
            return
        for r in rows:
            result.setItem(r.label,handler(row=r.value,row_attr=r.attr,**kwargs))
        return result




class TemplateGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGrid,gnrcomponents/tpleditor:ChunkEditor'
    @struct_method
    def fgr_templateGrid(self,pane,pbl_classes='*',fields=None,contentCb=None,template=None,template_resource=None,**kwargs):
        def struct(struct):
            r = struct.view().rows()
            r.cell('tpl',rowTemplate=template or '=.current_template',width='100%',
                    edit=dict(fields=fields,contentCb=contentCb) if fields or contentCb else None,
                    calculated=True)
        frame = pane.bagGrid(pbl_classes=pbl_classes,struct=struct,**kwargs)

        if template_resource:
            frame.grid.data('.current_template',self.loadTemplate(template_resource))
            if self.isDeveloper():
                frame.grid.attributes['connect_onCellDblClick'] = "if($1.shiftKey){this.publish('editRowTemplate')}"
                #frame.grid.dataFormula('.fakeTplData',"new gnr.GnrBag();",_onBuilt=1)
                frame.grid.templateChunk(template=template_resource,
                            datasource='^.fakeTplData',
                            editable=True,hidden=True,
                            **{'subscribe_%s_editRowTemplate' %frame.grid.attributes['nodeId']:"this.publish('openTemplatePalette');"})
        return frame

        