# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs

class FrameGridSlots(BaseComponent):
    @struct_method
    def fgr_slotbar_export(self,pane,_class='iconbox export',mode='xls',enable=None,rawData=True,**kwargs):
        kwargs.setdefault('visible',enable)
        return pane.slotButton(label='!!Export',publish='serverAction',command='export',opt_export_mode=mode or 'xls',
                                opt_rawData=rawData, iconClass=_class,**kwargs) 
       
    @struct_method
    def fgr_slotbar_addrow(self,pane,_class='iconbox add_row',disabled='^.disabledButton',enable=None,delay=300,**kwargs):
        kwargs.setdefault('visible',enable)
        return pane.slotButton(label='!!Add',publish='addrow',iconClass=_class,disabled=disabled,
                                _delay=delay,**kwargs)
         
    @struct_method
    def fgr_slotbar_delrow(self,pane,_class='iconbox delete_row',enable=None,disabled='^.disabledButton',**kwargs):
        kwargs.setdefault('visible',enable)
        return pane.slotButton(label='!!Delete',publish='delrow',iconClass=_class,disabled=disabled,**kwargs)
    
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
        return pane.slotButton(label='!!Save',publish='saveChangedRows',command='export',
                               disabled='==status!="changed"',iconClass="iconbox save",
                                status='^.grid.editor.status',**kwargs)
    @struct_method
    def fgr_slotbar_gridsemaphore(self,pane,**kwargs):
        return pane.div(_class='editGrid_semaphore',padding_left='4px')
                                
class FrameGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGridSlots'
    @extract_kwargs(top=True,grid=True)
    @struct_method
    def fgr_frameGrid(self,pane,frameCode=None,struct=None,storepath=None,structpath=None,
                    datamode=None,table=None,grid_kwargs=True,top_kwargs=None,iconSize=16,
                    _newGrid=None,**kwargs):
        frame = pane.framePane(frameCode=frameCode,center_overflow='hidden',**kwargs)
        grid_kwargs.setdefault('_newGrid',_newGrid)
        grid_kwargs.setdefault('structpath',structpath)
        grid_kwargs.setdefault('sortedBy','^.sorted')
        grid_kwargs['selfsubscribe_addrow'] = grid_kwargs.get('selfsubscribe_addrow','this.widget.addRows($1._counter,$1.evt);')
        grid_kwargs['selfsubscribe_delrow'] = grid_kwargs.get('selfsubscribe_delrow','this.widget.deleteSelectedRows();')
        grid_kwargs['selfsubscribe_setSortedBy'] = """this.setRelativeData(this.attr.sortedBy,$1);"""
        frame.includedView(autoWidth=False,
                          storepath=storepath,datamode=datamode,
                          datapath='.grid',selectedId='.selectedId',
                          struct=struct,table=table,
                          **grid_kwargs)
        if top_kwargs:
            top_kwargs['slotbar_view'] = frame
            frame.top.slotToolbar(**top_kwargs)
        return frame

    @extract_kwargs(default=True)
    @struct_method
    def fgr_bagGrid(self,pane,storepath=None,title=None,default_kwargs=None,pbl_classes=None,gridEditor=True,**kwargs):
        if pbl_classes:
            kwargs['_class'] = 'pbl_roundedGroup'
        if gridEditor:
            kwargs['grid_gridEditor'] = dict(default_kwargs=default_kwargs)
        frame = pane.frameGrid(_newGrid=True,datamode='bag',title=title,**kwargs)
        if pbl_classes:
            frame.top.slotBar('5,vtitle,*,delrow,addrow,2',vtitle=title,_class='pbl_roundedGroupLabel')
        else:
            frame.top.slotToolbar('5,vtitle,*,delrow,addrow,2',vtitle=title)

        store = frame.grid.bagStore(storepath=storepath)
        frame.store = store
        return frame

class BagGrid(BaseComponent):
    pass

        