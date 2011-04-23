# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrlang import extract_kwargs

    
class FrameGridSlots(BaseComponent):
    py_requires='gnrcomponents/grid_configurator/grid_configurator:GridConfigurator'
    @struct_method
    def fgr_slotbar_export(self,pane,_class='buttonIcon icnBaseExport',mode='xls',enable=None,**kwargs):
        return pane.slotButton(label='!!Export',publish='serverAction',command='export',opt_export_mode=mode or 'xls',
                                baseClass='no_background',iconClass=_class,visible=enable,**kwargs) 
       
    @struct_method
    def fgr_slotbar_addrow(self,pane,_class='icnBaseAdd',enable=None,parentForm=True,delay=300,**kwargs):
        return pane.slotButton(label='!!Add',publish='addrow',baseClass='no_background',iconClass=_class,visible=enable,parentForm=parentForm,
                                _delay=delay,**kwargs)
         
    @struct_method
    def fgr_slotbar_delrow(self,pane,_class='icnBaseDelete',enable=None,parentForm=True,**kwargs):
        return pane.slotButton(label='!!Delete',publish='delrow',baseClass='no_background',iconClass=_class,visible=enable,parentForm=parentForm,**kwargs)
    
    @struct_method
    def fgr_slotbar_updrow(self,pane,_class='icnBaseEdit',enable=None,parentForm=True,**kwargs):
        return pane.slotButton(label='!!Delete',publish='updrow',baseClass='no_background',iconClass=_class,visible=enable,parentForm=parentForm,**kwargs)


    @struct_method
    def fgr_slotbar_gridConfigurator(self,pane,_class='gridConfigurator',frameCode=None,enable=None,parentForm=True,**kwargs):
        pane.div(tip='!!Config view', _class=_class,visible=enable,width='100%',_gridConfigurator=True,**kwargs)
        
    @struct_method
    def fgr_slotbar_tools(self,pane,_class='icnBaseArrowDown',enable=None,frameCode=None,**kwargs):
        return pane.slotButton(label='!!Grid options',publish='tools',target='%s_frame' %frameCode,
                                baseClass='no_background',iconClass=_class,visible=enable,
                                **kwargs)



class FrameGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGridSlots'
    @extract_kwargs(top=True,grid=True)
    @struct_method
    def fgr_frameGrid(self,pane,frameCode=None,struct=None,grid_kwargs=True,top_kwargs=None,**kwargs):
        kwargs['selfsubscribe_tools'] = """ var bc = this.getWidget();
                                            genro.dom.toggleClass(bc._left,"visibleBcPane"); 
                                            bc._layoutChildren("left");
                                            """
        frame = pane.framePane(frameCode=frameCode,center_overflow='hidden',**kwargs)
        if top_kwargs:
            frame.top.slotToolbar(**top_kwargs)
        frame.left.leftBar()
        iv = frame.includedView(autoWidth=False,datapath='.grid',selectedId='.selectedId',
                                struct=struct,sortedBy='^.sorted',
                                 _newGrid=True,**grid_kwargs)
        return frame

    @struct_method
    def fgr_leftBar(self,pane):
        pane.slotToolbar('5,gridConfigurator,10,export,*')
        pane.attributes['_class'] = 'hiddenBcPane'
        
    def fgr_relationHandler(self,pane,frameCode=None,struct=None,grid_kwargs=True,top_kwargs=None,**kwargs):
        pass
        