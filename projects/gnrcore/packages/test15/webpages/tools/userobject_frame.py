# -*- coding: utf-8 -*-

import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                    gnrcomponents/userobject/userobject_editor:GroupByEditor"""
    
    def test_1_userobject_frame(self, pane):
        pane.UserObjectLayout(table='fatt.fattura',pkg='fatt',objtype='query',height='300px',width='400px',
                            border='1px solid silver',
                            configurator={'region':'left','splitter':True,
                                        'border_right':'1px solid #ccc','width':'230px'})

    def test_2_userobject_bar(self, pane):
        frame = pane.framePane(height='300px',width='400px',border='1px solid silver',rounded=10)
        frame.top.userObjectBar(table='fatt.fattura',objtype='fakeobject',
                                source_mieidati='=.mieidati',
                                mainIdentifier='test_2')

        bc = frame.center.borderContainer(datapath='.mieidati')
        fb = bc.contentPane(region='top').formbuilder()
        fb.textbox(value='^.nome',lbl='Nome')
        grid = bc.contentPane(region='center').quickGrid(value='^.righe')
        grid.tools('delrow,addrow',title='Prova')
        grid.column('code',name='Code',width='5em',edit=True)
        grid.column('description',name='Description',width='20em',edit=True)

    def test_3_userobject_groupbyusage(self, pane):
        pane.groupByEditor(table='fatt.fattura_riga',height='600px',width='900px')
