# -*- coding: utf-8 -*-

import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_userobject_frame(self, pane):
        pane.UserObjectLayout(table='fatt.fattura',pkg='fatt',objtype='query',height='300px',width='400px',
                            border='1px solid silver',
                            configurator={'region':'left','splitter':True,
                                        'border_right':'1px solid #ccc','width':'230px'})

    def test_2_userobject_bar(self, pane):
        frame = pane.framePane(height='300px',width='400px',border='1px solid silver',rounded=10)
        frame.top.userObjectBar(table='fatt.fattura',pkg='fatt',objtype='fakeobject',
                                source_mieidati='=.mieidati',favoriteIdentifier='test_2')
        bc = frame.center.borderContainer(datapath='.mieidati')
        fb = bc.contentPane(region='top').formbuilder()
        fb.textbox(value='^.nome',lbl='Nome')
        grid = bc.contentPane(region='center').quickGrid(value='^.righe')
        grid.tools('delrow,addrow',title='Prova')
        grid.column('code',name='Code',width='5em',edit=True)
        grid.column('description',name='Description',width='20em',edit=True)