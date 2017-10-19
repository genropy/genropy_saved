# -*- coding: UTF-8 -*-

# Copyright (c) 2011 Softwell. All rights reserved.

"""Datetextbox & datetime"""
from datetime import datetime

class GnrCustomWebPage(object):
    dojo_source=True
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'DateTextBox'
        

    def test_0_base(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.dateTextBox(value='^.date_from',lbl='Date from',period_to='.date_to')
        fb.dateTextBox(value='^.date_to',lbl='Date to')


    def test_1_pupup(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.dateTextBox(value='^.date_1',lbl='Date 1',pivotYear=1)
        fb.dateTextBox(value='^.date_2',lbl='Date 2',popup=False)
        fb.dateTextBox(value='^.date_3',lbl='Date 3',noIcon=True)
        fb.dateTextBox(value='^.date_4',lbl='Date 4',noIcon=True,popup=False)

    def test_2_datetime(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.dataFormula('.datetime',"new Date();",_onStart=True)
        fb.dataFormula('.datetime_sec',"new Date();",_onStart=True)
        fb.data('.datetime_static',datetime.now())

        fb.datetimeTextbox(value='^.datetime',lbl='Datetime',datetime=True)
        fb.datetimeTextbox(value='^.datetime_sec',lbl='Datetime sec',seconds=True)
        fb.datetimeTextbox(value='^.datetime_static',lbl='Datetime static',seconds=True)