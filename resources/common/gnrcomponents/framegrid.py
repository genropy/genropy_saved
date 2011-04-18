# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrlang import extract_kwargs

class FrameGridSlots(BaseComponent):
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
                                            bc._layoutChildren("left");"""
        frame = pane.framePane(frameCode=frameCode,center_overflow='hidden',**kwargs)
        if top_kwargs:
            frame.top.slotToolbar(**top_kwargs)
        left = frame.left
        left.slotToolbar('export,updrow')
        left.attributes['_class'] = 'hiddenBcPane'
        iv = frame.includedView(autoWidth=False,datapath='.grid',selectedId='.selectedId',
                                struct=struct,sortedBy='^.sorted',
                                 _newGrid=True,**grid_kwargs)
        return frame
        
    def fgr_relationHandler(self,pane,frameCode=None,struct=None,grid_kwargs=True,top_kwargs=None,**kwargs):
        pass

        
        
class IncludedView(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGrid'
    
    """
     add_action=None, add_class='buttonIcon icnBaseAdd', add_enable='^form.canWrite',
     del_action=None, del_class='buttonIcon icnBaseDelete', del_enable='^form.canWrite',
     upd_action=None, upd_class='buttonIcon icnBaseEdit', upd_enable='^form.canWrite',
     close_action=None, close_class='buttonIcon icnTabClose',
     print_action=None, print_class='buttonIcon icnBasePrinter',
     pdf_action=None, pdf_class='buttonIcon icnBasePdf', pdf_name=None,
     export_action=None, export_class='buttonIcon icnBaseExport',
     tools_action=None, tools_class='buttonIcon icnBaseAction',
     tools_enable='^form.canWrite', tools_lbl=None,
    
    
     parentBC,        #diventa contentPane  
     nodeId=None,     #va a finire sulla griglia
     table=None,      #va a finire sulla griglia 
     datapath=None,   #va a finire sul frame
     storepath=None,  #diventera uno store?
     selectionPars=None,  #assert mettici un tableviewer o un tablehandler
     formPars=None, #assert mettici un tablehandler
     label=None,    #se testo lo mettiamo nella toolbar se callable assert adattamento complesso
     caption=None,  #adattato tramite parentBc
     
     footer=None,   #assert usa .bottom
     
     lock_action=False,  #assert non ha senso
     _onStart=False, #assert not
     filterOn=None,  #diventa searchOn
     pickerPars=None, #assert 
     centerPaneCb=None, #assert
     editorEnabled=None, #va alla griglia
      parentLock='^status.locked',  #assert
      reloader=None, #assert
      externalChanges=None, #assert
      addOnCb=None, #assert
      zoom=True, #assert
      hasToolbar=False, #assert
      canSort=True, #va alla griglia
      configurable=None, #assert
       dropCodes=None, #alla griglia gestito da webstruct usa  va a draganddrop della griglia
    
        
    """
    @extract_kwargs(_dictkwargs={'add':True,'del':True,'upd':True,'print':True,'export':True,'tools':True,'top':True})
    def includedViewBox(self, parentBC, nodeId=None,frameCode=None,datapath=None,struct=None,table=None, 
                        storepath=None, label=None, caption=None,filterOn=None,editorEnabled=None,canSort=True,dropCodes=None,
                        add_kwargs=None,del_kwargs=None,upd_kwargs=None,print_kwargs=None,export_kwargs=None,tools_kwargs=None,
                        top_kwargs=None,**kwargs):         
        assert not 'selectionPars' in kwargs, 'use tableviewer instead of or attach a selectionStore'
        assert not 'formPars' in kwargs, 'no longer supported'
        assert not 'lock_action' in kwargs, 'no longer supported'
        assert not 'footer' in kwargs, 'no longer supported'
        assert not '_onStart' in kwargs, 'no longer supported'
        assert not 'pickerPars' in kwargs, 'no longer supported'
        assert not 'centerPaneCb' in kwargs, 'no longer supported'
        assert not 'parentLock' in kwargs, 'no longer supported'
        assert not 'reloader' in kwargs, 'no longer supported'
        assert not 'externalChanges' in kwargs, 'no longer supported'
        assert not 'addOnCb' in kwargs, 'no longer supported'
        assert not 'hasToolbar' in kwargs, 'no longer supported'
        assert not 'zoom' in kwargs, 'no longer supported'
        assert not 'configurable' in kwargs, 'no longer supported'
        assert not print_kwargs, 'provided by default'
        assert not export_kwargs, 'provided by default'
        assert (frameCode or nodeId), 'nodeId or frameCode must be provided'
        assert storepath,'this adapter is for grid with storepath'
        
        parentBC.attributes['tag'] = 'ContentPane'
        pane = parentBC
        frameCode = frameCode or 'frame_%s' %nodeId
        datapath = datapath or '#FORM.%s' %frameCode
        frame = pane.frameGrid(frameCode=frameCode,datapath=datapath,struct=struct,
                                grid_nodeId=nodeId,grid_table=table,**kwargs)
        storepath = '#FORM.record%s' %storepath
       # frame.bagStore(storepath=storepath,table=table)
        gridattr = frame.grid.attributes
        gridattr['storepath'] = storepath
        gridattr['selfsubscribe_addrow'] = """for(var i=0; i<$1._counter;i++){
                                                this.widget.addBagRow('#id', '*', this.widget.newBagRow(),$1.evt);
                                              }
                                              this.widget.editBagRow(null);"""
        gridattr['selfsubscribe_delrow'] = """this.widget.delBagRow('*', true);FIRE .onDeletedRow;"""
        gridattr['tag'] = 'includedview'
        if dropCodes:
            frame.grid.dragAndDrop(dropCodes)
        slots = ['tools,2']
        slotsKw = {}
        if label:
            slots.append('label,*')
            slotsKw['label'] = label
        else:
            slots.append('*')
        if add_kwargs:
            action = add_kwargs.get('action')
            slots.append('addrow')
            assert not isinstance(action,basestring), 'custom action are not supported'
        if del_kwargs:
            action = add_kwargs.get('action')
            slots.append('delrow')
            assert not isinstance(action,basestring), 'custom action are not supported'
        frame.top.slotToolbar(','.join(slots),**slotsKw)        
        return frame.grid
  
            
