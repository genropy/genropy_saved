# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class TemplateEditor(BaseComponent):
    py_requires='foundation/macrowidgets:RichTextEditor,gnrcomponents/framegrid:FrameGrid'
    css_requires='public'
    @struct_method
    def te_templateEditor(self,pane,storepath=None,maintable=None,**kwargs):
        frame = pane.framePane(datapath='.template_editor',border='1px solid gray',rounded=4)
        frame.top.slotToolbar(slots='*,stackButtons,*')
        sc = frame.center.stackContainer()
        self._te_frameEdit(sc.framePane(title='!!Edit'),table=maintable)
        self._te_framePreview(sc.framePane(title='!!Preview'))
    
    def _te_frameEdit(self,frame,table=None):
        bc = frame.center.borderContainer()
        def struct(struct):
            r = struct.view().rows()
            r.cell('fieldname', name='Field', width='100%')
            r.cell('varname', name='As', width='10em')
            r.cell('format', name='Format', width='10em')

        left = bc.borderContainer(region='left',width='300px')
        framegrid = left.frameGrid(frameCode='varsgrid_#',height='200px',region='bottom',splitter=True,storepath='.varsbag',
                del_action=True,label='!!Template Variables',struct=struct,datamode='bag',_class='pbl_roundedGroup',margin='3px')
        
        tablecode = table.replace('.','_')
        dropCode = 'gnrdbfld_%s' %tablecode
        editor = framegrid.grid.gridEditor()
        editor.textbox(gridcell='varname')
        editor.textbox(gridcell='format')
        framegrid.top.div('!!Variables',_class='pbl_roundedGroupLabel')
        framegrid.grid.dragAndDrop(dropCodes=dropCode)
        framegrid.grid.dataController("""var caption = data.fullcaption;
                                var varname = caption.replace(/\W/g,'_').toLowerCase()
                                grid.addBagRow('#id', '*', grid.newBagRow({'fieldpath':data.fieldpath,fieldname:caption,varname:varname,virtual_column:data.virtual_column}));""",
                             data="^.dropped_%s" %dropCode,grid=framegrid.grid.js_widget)
        
        
        frametree= left.framePane(region='center',margin='2px',margin_bottom='4px',_class='pbl_roundedGroup')
        frametree.fieldsTree(table=table,trash=False)        
        frametree.top.div('!!Fields',_class='pbl_roundedGroupLabel')
        self.RichTextEditor(bc.contentPane(region='center'), value='^.content',
                            toolbar=self.rte_toolbar_standard())
                            
    def _te_framePreview(self,frame):
        frame.div('preview')
