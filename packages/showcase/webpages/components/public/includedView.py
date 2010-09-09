#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="foundation/includedview"
    def main(self, root, **kwargs):        
        tc = root.tabContainer()
        # self.ivDbSelection(tc, title="Db Selection")
        self.ivInline(tc, title="Inline")
    
    def ivInline(self, parent, **kwargs):
        """An includedview on a datastore's path."""
        bc = parent.borderContainer(**kwargs)
        
        b = Bag()
        b.addItem('r0',Bag(dict(name="name", description="Full name", size=40, type="U")))
        b.addItem('r1',Bag(dict(name="birth date", description="Birth date", size=10, type="D")))
        
        bc.data('inline_data', b)
        
        def structInlineData(struct):
            r = struct.view().rows()
            r.cell('name', name='!!Name', width='20ex')
            r.cell('description', name='!!Description', width='40ex')
            r.cell('size', name='!!Size', width='5ex')
            r.cell('type', name='!!Type', width='20ex')
        
        iv = self.includedViewBox(bc,label='!!Inline IncludedView', locked=False,
                            datamode="bag",
                            storepath='inline_data', struct=structInlineData,
                            autoWidth=True, add_action=True,del_action=True)
        ge = iv.gridEditor()
        ge.textbox(gridcell="name")
        ge.textbox(gridcell="description")
        ge.numberspinner(gridcell="size", min=1, max=100)
        ge.filteringselect(gridcell="type", values="I:Int,R:Real,S:String,U:Unicode,D:Date,H:Time,DH:Date and Time,X:Bag")