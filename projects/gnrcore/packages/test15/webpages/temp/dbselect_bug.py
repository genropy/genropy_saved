# -*- coding: utf-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from builtins import object
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from time import sleep

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_combobug(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbCombobox(dbtable='adm.user',value='^.user',lbl='dbCombo',
                    width='25em',hasDownArrow=True)
        fb.combobox(value='^.combobox',values='Pippo,Pluto,Paperino',lbl='Combo')

        fb.filteringSelect(value='^.filtering',values='pippo:Pippo,pluto:Pluto,paperino:Paperino',lbl='Filtering')

    def test_1_firsttest(self,pane):
        """dbselect with auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='adm.user',value='^.user_id',lbl='User',
                    auxColumns='$email',
                    selected_username='.username',width='25em',
                    hasDownArrow=True)
        fb.textbox(value='^.foo',lbl='Foo')
        fb.textbox(value='^.bar',lbl='bar')

        fb.dbCombobox(dbtable='adm.user',value='^.username',lbl='Combo',
                    selected_username='.username',width='25em',
                    hasDownArrow=True)

        fb.dbSelect(dbtable='adm.user',value='^.user_id_2',lbl='zzz',
                    auxColumns='$username',width='25em',
                    hasDownArrow=True)
        #fb.data('.username','...')
        #fb.div('^.user_id',lbl='User')
        #fb.dataController("genro.bp(true);",user_id='^.user_id')
        fb.div('^.username',lbl='Username')

