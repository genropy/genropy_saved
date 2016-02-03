# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.
# Frameindex component

from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class ShortcutGrid(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGrid'

    @struct_method
    def sh_shortcutGrid(self,pane,code=None,title=None,**kwargs):
        pkgId = pane.getInheritedAttributes().get('pkgId')
        code = code or '_mainshortcuts_'
        code = '%s_%s' %(pkgId,code)
        pane.bagGrid(frameCode=code,storepath='#ANCHOR.shortcuts.%s' %code,
                    struct=self.sh_struct,title=title or '!!Shortcuts',
                    datapath='shortcuts.%s' %code,
                    pbl_classes=True,**kwargs)

    def sh_struct(self,struct):
        r = struct.view().rows()
        r.cell('shortcut',width='8em',name='Shortcut',edit=True)
        r.cell('phrase',width='20em',name='Phrase',edit=True)
        r.cell('group',width='10em',name='Group',edit=True)
