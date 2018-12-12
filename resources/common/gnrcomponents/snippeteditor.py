# -*- coding: utf-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method

class SnippetEditor(BaseComponent):
    @struct_method
    def sn_snippetEditor(self,pane,frameCode=None,datapath=None,**kwargs):
        pane.attributes.update(overflow='hidden')
        form = pane.frameForm(frameCode=frameCode,
                        datapath=datapath or '.snippet',
                        store='document')
        grid = form.record.quickGrid('^.content')
        grid.column(name='name',width='10em',edit=True)
        grid.column(name='snippet',width='50em',edit=dict(tag='simpleTextArea'))
        return form
