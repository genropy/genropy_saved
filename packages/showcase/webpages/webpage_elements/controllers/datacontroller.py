# -*- coding: UTF-8 -*-

# dataController.py
# Created by Filippo Astolfi on 2010-10-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataController"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_basic(self, pane):
        """dataController"""
        bc = pane.borderContainer(height='200px')

        bc.div('In this basic example we want to show you two equivalent syntax to write the dataController:',
               font_size='.9em', text_align='justify')
        bc.div("""1) The first syntax is fb.dataController(\"SET .aaa=\'positive number\'\" ,_if='shooter>=0',
                     _else=\"SET .aaa=\'negative number\'\",shooter=\'^.x\') """,
               font_size='.9em', text_align='justify')
        bc.div("""2) The second syntax is fb.dataController(\"\"\"if(shooter>=0){SET .bbb=\'positive number\';}
                     else{SET .bbb=\'negative number\';}\"\"\",shooter=\'^.y\');""",
               font_size='.9em', text_align='justify')

        fb = bc.formbuilder(cols=3, datapath='test1')

        fb.dataController("SET .aaa='positive number'", _if='shooter>=0',
                          _else="SET .aaa='negative number'", shooter='^.x')
        fb.div('1)', font_size='.9em', text_align='justify')
        fb.numberTextbox(value='^.x', lbl='x')
        fb.textbox(value='^.aaa', margin='10px', lbl='aaa')

        fb.dataController("""if(shooter>=0){SET .bbb='positive number';}
                               else{SET .bbb='negative number';}""",
                          shooter='^.y')
        fb.div('2)', font_size='.9em', text_align='justify')
        fb.numberTextbox(value='^.y', lbl='y')
        fb.textbox(value='^.bbb', margin='10px', lbl='bbb')

    def test_2_advanced(self, pane):
        """dataController - remote control"""
        bc = pane.borderContainer(height='350px', datapath='test2')
        top = bc.contentPane(region='top', height='100px')
        top.button('Build', fire='.build')

        top.button('Add element', fire='.add')
        top.dataController("""var pane = genro.nodeById('remoteContent')
                              pane._('div',{height:'200px',width:'200px',background:'lightBlue',
                                            border:'1px solid blue','float':'left',
                                            remote:{'method':'test'}});
                           """, _fired="^.add")

        center = bc.contentPane(region='center').div(nodeId='remoteContent')
        center.div().remote('test', _fired='^.build')

    def remote_test(self, pane, **kwargs):
        print 'remote test executed!'
        pane.div('hello', height='40px', width='80px', background='lime')
        