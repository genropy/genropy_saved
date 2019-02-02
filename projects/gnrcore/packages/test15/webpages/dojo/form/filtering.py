# -*- coding: utf-8 -*-

# filtering.py
# Created by Francesco Porcari on 2011-10-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"FilteringSelect"
from builtins import object
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    dojo_source=True
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''

    def isDeveloper(self):
        return True
         

    def test_1_filtering(self,pane):
        "FilteringSelect"
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.data('.code','1')
        fb.button('Reset value',action='SET .pluto=null;')
        fb.filteringSelect(value='^.code',values='0:Zero,1:One,2:Two',lbl='With code')
        fb.filteringSelect(value='^.description',values='Zero,One,Two',lbl='No code')

    def test_2_filtering(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        b = Bag()
        b.setItem('r1',None,caption='Foo',id='A')
        b.setItem('r2',None,caption='Bar',id='B')
        b.setItem('r3',None,caption='Spam',id='C')
        fb.data('.store',b)
        fb.filteringSelect(value='^.tbag',lbl='Test bag 1',storepath='.store')

    def test_3_filtering(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        b = Bag()
        b.setItem('r1',None,caption='Foo',code='A')
        b.setItem('r2',None,caption='Bar',code='B')
        b.setItem('r3',None,caption='Spam',code='C')
        fb.data('.store',b)
        fb.filteringSelect(value='^.tbag',lbl='Test bag 2',storepath='.store',
                            storeid='code')

    def test_4_filtering(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        b = Bag()
        b.setItem('A',None,caption='Foo')
        b.setItem('B',None,caption='Bar')
        b.setItem('C',None,caption='Spam')
        fb.data('.store',b)
        fb.filteringSelect(value='^.tbag',lbl='Test bag 3',storepath='.store',
                            storeid='#k')


    def test_2_combobox(self,pane):
        "combobox"
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.comboBox(value='^.description',values='Zero,One,Two',lbl='Combo')

