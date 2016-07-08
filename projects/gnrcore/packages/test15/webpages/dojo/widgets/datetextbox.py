# -*- coding: UTF-8 -*-

# tree.py
# Created by Filippo Astolfi on 2011-12-02.
# Copyright (c) 2011 Softwell. All rights reserved.

"""numberTextBox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'DateTextBox'
        

    def test_0_base(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.dateTextBox(value='^.date_from',lbl='Date from',period_to='.date_to')
        fb.dateTextBox(value='^.date_to',lbl='Date to')


    def test_0_pupup(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.dateTextBox(value='^.date_1',lbl='Date 1')
        fb.dateTextBox(value='^.date_2',lbl='Date 2',popup=False)
        fb.dateTextBox(value='^.date_3',lbl='Date 3',noIcon=True)
        fb.dateTextBox(value='^.date_4',lbl='Date 4',noIcon=True,popup=False)
