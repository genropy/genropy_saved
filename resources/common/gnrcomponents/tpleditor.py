# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-06-22.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class TemplateEditor(BaseComponent):
    @struct_method
    def te_templateEditor(self,pane,storepath=None,maintable=None,**kwargs):
        frame = pane.framePane(datapath='.template_editor')
        toolbar = frame.top.slotToolbar(slots='lcol,*,rcol')
        bc = frame.center.borderContainer()
        toolbar.lcol.slotButton('Fields',action='bc.setRegionVisible("left","toggle");',bc=bc.js_widget)
        toolbar.rcol.slotButton('Preview',action='bc.setRegionVisible("right","toggle");',bc=bc.js_widget)
        leftbc = bc.borderContainer(region='left',width='300px',hidden=True)
        self.fieldstree(leftbc.contentPane(region='top',height='50%',datapath='.fields',
                                            splitter=True,_class='pbl_roundedGroup',margin='3px'))
        self.varsgrid(leftbc.contentPane(region='center',margin='3px',margin_top='4px'))
        self.previewpane(bc.framePane(region='right',hidden=True,width='600px'))
        self.RichTextEditor(bc.contentPane(region='center'),value='^.source')    