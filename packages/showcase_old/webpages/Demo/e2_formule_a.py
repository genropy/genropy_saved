#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.web.gnrwebpage import GnrWebPage

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=2)
        fb.horizontalslider(lbl='!!Base', value = '^base', width='200px', 
                                         minimum=1, maximum=100)
        fb.numberTextBox(value='^base', places=2)
        fb.horizontalslider(lbl='!!Height', value = '^height', width='200px', 
                                         minimum=1, maximum=100)
        fb.numberTextBox(value='^height', places=2)
        fb.dataFormula('area', 'base * height', base='^base', height='^height')
        fb.numberTextBox(lbl='!!Area', value = '^area',border='1px solid grey',padding='2px')
       
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
