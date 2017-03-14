# -*- coding: UTF-8 -*-

# sharedobjects.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.xtnd.gnrpandas import PandasSharedObject


        
"Test sharedobjects"
class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,
                  js_plugins/statspane/statspane:PdCommandsGrid"""
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        pane.sharedObject('mydata',shared_id='so_test1')
        fb=pane.formbuilder(cols=1, datapath='mydata')
        fb.textbox('^.name', lbl='Name')
        fb.textbox('^.address', lbl='Address')
        fb.numbertextbox('^.age', lbl='Age')


    def test_1_pandasSharedObject(self,pane):
        pane.sharedObject('.so_test',shared_id='so_test6',factory=PandasSharedObject,
                        nodeId='so_panda',autoSave=True,autoLoad=True)

        pane.pdCommandsGrid('test_3',height='300px',width='800px',storepath='#so_panda.so_test.commands')

    

