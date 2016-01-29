# -*- coding: UTF-8 -*-
# 
"""Generc lbl"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler"

    def test_1_textbox(self, pane):
        """generic lbl"""
        pane.attributes.update(lbl_side='top')
        pane.textbox(value='^.nome',lbl='Chi sei')
        pane.br()
        pane.br()

        pane.simpleTextarea(value='^.area',lbl='Prova area',width='200px')

        #pane.field('fatt.cliente.ragione_sociale')

    def test_2_slotBar(self, pane):
        f = pane.frameForm(height='200px',width='400px')
        f.slotToolbar()
