# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from time import sleep

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         

    def test_0_tableinpalette(self,pane):
        palette = pane.palettePane(paletteCode='test',dockButton=True,height='400px',width='280px',right='20px',top='20px',
                                palette_persist=False)  
        fb = palette.formbuilder(cols=1,lblpos='T',lbl_text_align='center',
                                lbl_background='gray',
                                lbl_color='white',
                                style='border:1px solid silver;border_collapse:collapse',
                                margin='3px',border_spacing='0px')
        fb_comp = fb.formbuilder(cols=1,lbl='Competenza')
        fb_comp.textbox(value='^.competenza',lbl='Periodo')

        fb_ded = fb.formbuilder(cols=1,lbl='Deducibilità')
        fb_ded.numberTextBox(value='^.irpef',lbl='Irpef/Irpeg')
        fb_ded.numberTextBox(value='^.irap',lbl='Irap')


        fb_cesp = fb.formbuilder(cols=1,lbl='Gestione cespiti')
        fb_cesp.textbox(value='^.cespite',lbl='Cespite')
