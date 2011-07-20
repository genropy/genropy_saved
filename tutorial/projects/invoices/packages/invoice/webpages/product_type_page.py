#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2011-07-20.
Copyright (c) 2008 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    maintable = 'invoice.product_type'
    py_requires = 'public:TableHandlerMain'
    
    def th_form(self, form):
        pane = form.record.contentPane()
        fb = pane.formbuilder(cols=2)
        fb.field('code',width='7em')
        fb.field('description',width='20em')