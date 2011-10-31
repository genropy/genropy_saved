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
    def fgr_slotbar_addrow(self,pane,_class='iconbox add_row',enable=None,disabled='^.disabledButton',delay=300,**kwargs):
        return pane.slotButton(label='!!Add',publish='addrow',iconClass=_class,visible=enable,disabled=disabled,
                                _delay=delay,**kwargs)
         
    @struct_method
    def fgr_slotbar_delrow(self,pane,_class='iconbox delete_row',enable=None,disabled='^.disabledButton',**kwargs):
        return pane.slotButton(label='!!Delete',publish='delrow',iconClass=_class,visible=enable,disabled=disabled,**kwargs)
    
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
    def _fgr_standard_addrow(self):
        return """for(var i=0;i<$1._counter;i++){this.widget.addBagRow('#id', '*', this.widget.newBagRow(),$1.evt);}this.widget.editBagRow(null);"""
        
    def _fgr_standard_delrow(self):
        return """this.widget.delBagRow('*', true);"""

class FrameGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGridSlots'
    @extract_kwargs(top=True,grid=True)
    @struct_method
    def fgr_frameGrid(self,pane,frameCode=None,struct=None,storepath=None,structpath=None,datamode=None,table=None,grid_kwargs=True,top_kwargs=None,iconSize=16,**kwargs):
        frame = pane.framePane(frameCode=frameCode,center_overflow='hidden',**kwargs)
        _newGrid= False if datamode=='bag' else True
        grid_kwargs.setdefault('_newGrid',_newGrid)
        grid_kwargs.setdefault('structpath',structpath)
        if top_kwargs:
            top_kwargs['slotbar_view'] = frame
            frame.top.slotToolbar(**top_kwargs)
        if datamode=='bag':
            grid_kwargs['selfsubscribe_addrow'] = grid_kwargs.get('selfsubscribe_addrow',self._fgr_standard_addrow())
            grid_kwargs['selfsubscribe_delrow'] =  grid_kwargs.get('selfsubscribe_delrow',self._fgr_standard_delrow())
        else:
            grid_kwargs['selfsubscribe_delrow'] = grid_kwargs.get('selfsubscribe_delrow','this.widget.deleteRows();')
        frame.includedView(autoWidth=False,
                          storepath=storepath,datamode=datamode,
                          datapath='.grid',selectedId='.selectedId',
                          struct=struct,sortedBy='^.sorted',table=table,
                          **grid_kwargs)
        return frame
        