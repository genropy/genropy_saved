# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs

    
class FrameGridSlots(BaseComponent):
    py_requires='gnrcomponents/grid_configurator/grid_configurator:GridConfigurator'
    @struct_method
    def fgr_slotbar_export(self,pane,_class='iconbox export',mode='xls',enable=None,**kwargs):
        return pane.slotButton(label='!!Export',publish='serverAction',command='export',opt_export_mode=mode or 'xls',
                                iconClass=_class,visible=enable,**kwargs) 
       
    @struct_method
    def fgr_slotbar_addrow(self,pane,_class='iconbox add_row',enable=None,delay=300,**kwargs):
        return pane.slotButton(label='!!Add',publish='addrow',iconClass=_class,visible=enable,disabled='^.disabledButton',
                                _delay=delay,**kwargs)
         
    @struct_method
    def fgr_slotbar_delrow(self,pane,_class='iconbox delete_row',enable=None,**kwargs):
        return pane.slotButton(label='!!Delete',publish='delrow',iconClass=_class,visible=enable,disabled=kwargs.pop('disabled','^.disabledButton'),**kwargs)
    
    @struct_method
    def fgr_slotbar_viewlocker(self, pane,frameCode=None,**kwargs):
       # kw['subscribe_%s_onLockChange' %storeId] = "this.widget.setIconClass($1.locked?'icnBaseLocked':'icnBaseUnlocked');"
        pane.slotButton('!!Locker',publish='viewlocker',iconClass='==_locked?"iconbox lock":"iconbox unlock";',_locked='^.locked',**kwargs)
    
    @struct_method
    def fgr_slotbar_updrow(self,pane,_class='icnBaseEdit',enable=None,parentForm=True,**kwargs):
        return pane.slotButton(label='!!Update',publish='updrow',iconClass=_class,visible=enable,parentForm=parentForm,**kwargs)

    @struct_method
    def fgr_slotbar_gridConfigurator(self,pane,_class='icnBaseTableEdit',frameCode=None,enable=None,parentForm=True,**kwargs):
        pane.div(tip='!!Configure view', _class=_class,visible=enable,_gridConfigurator=True,height='18px',width='20px',**kwargs)
        
    @struct_method
    def fgr_slotbar_gridTrashColumns(self,pane,_class='icnBaseTrash box24',frameCode=None,enable=None,parentForm=True,**kwargs):
        pane.div(tip='!!Drop here a column to remove it from the view', _class=_class,visible=enable,
        dropTarget=True, dropTypes='trashable', onDrop_trashable="""var sourceNode=genro.src.nodeBySourceNodeId(dropInfo.dragSourceInfo._id);
                                            if(sourceNode&&sourceNode.attr.onTrashed){
                                                funcCreate(sourceNode.attr.onTrashed,'data,dropInfo',sourceNode)(data,dropInfo);
                                            }""",**kwargs)


    @struct_method
    def fgr_slotbar_gridReload(self,pane,_class='icnFrameRefresh box16',enable=None,frameCode=None,**kwargs):
        return pane.slotButton(label='!!Reload',publish='reload',iconClass=_class,visible=enable,**kwargs)
        
    @struct_method
    def fgr_slotbar_tools(self,pane,_class='icnBaseArrowDown',enable=None,frameCode=None,**kwargs):
        return pane.slotButton(label='!!Grid options',publish='tools',target='%s_frame' %frameCode,
                                baseClass='no_background',iconClass=_class,visible=enable,
                                **kwargs)

class FrameGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGridSlots'
    @extract_kwargs(top=True,grid=True)
    @struct_method
    def fgr_frameGrid(self,pane,frameCode=None,struct=None,table=None,grid_kwargs=True,top_kwargs=None,iconSize=16,**kwargs):
        frame = pane.framePane(frameCode=frameCode,center_overflow='hidden',**kwargs)
        if top_kwargs:
            top_kwargs['slotbar_view'] = frame
            frame.top.slotToolbar(**top_kwargs)
        frame.includedView(autoWidth=False,
                                datapath='.grid',selectedId='.selectedId',
                                struct=struct,sortedBy='^.sorted',table=table,
                                selfsubscribe_delrow='this.widget.deleteRows();',
                                 **grid_kwargs)
        return frame
        