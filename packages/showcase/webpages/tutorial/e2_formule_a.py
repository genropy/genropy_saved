#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        fb = root.formbuilder(cols=2)
        fb.horizontalSlider(lbl='!!Base',value='^base',width='200px',
                            minimum=1,maximum=100)
        fb.numberTextBox(value='^base',places=2)
        fb.horizontalSlider(lbl='!!Altezza',value='^height',width='200px',
                            minimum=1,maximum=100)
        fb.numberTextBox(value='^height',places=2)
        fb.dataFormula('area','base * altezza', base='^base', altezza='^height')
        fb.numberTextBox(lbl='!!Area',value='^area',places=2,
                            border='2px solid grey',padding='2px')
