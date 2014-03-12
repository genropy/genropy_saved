# -*- coding: UTF-8 -*-

# tree.py
# Created by Filippo Astolfi on 2011-12-02.
# Copyright (c) 2011 Softwell. All rights reserved.

"""numberTextBox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'NumberTextBox'
        

    def test_0_base(self, pane):
        fb = pane.formbuilder(cols=2,datapath='.data')
        fb.numberTextbox(value='^.prova')
        fb.div('^.prova',lbl='Value')
        fb.button('Set base blank',action='SET .prova = "";')  
        fb.button('Set base',action='SET .prova = null;')  
        fb.button('Set container',action='SET .data = null;',datapath='.#parent')  

   #def test_1_base(self, pane):
   #    """Basic"""
   #    pane.div("""Ciao Ghi, ecco il test:""", margin_left='1em')
   #    pane.div("""1) Va sistemato l\'utilizzo dell\'attributo \"places\": attualmente
   #                funziona che se non specifichi \"places\" allora il campo accetta sia
   #                numeri senza cifre decimali sia numeri con fino a un massimo di 3 cifre
   #                decimali. Se invece viene specificato \"places\", allora l\'unico numero
   #                accettato è quel numero che ha il numero di cifre decimali specificate.
   #                Ad esempio, specificando \"places=3\", viene accettato SOLO un numero che
   #                abbia 3 cifre decimali.""", margin_left='1em')
   #    pane.div("""2) Inoltre se hai tempo, sistema anche l\'errata visualizzazione del punto
   #                esclamativo su sfondo rosso che compare in caso di errata compilazione:
   #                va a posizionarsi sopra il numero digitato...""", margin_left='1em')
   #    fb = pane.formbuilder(cols=2)
   #    fb.numberTextbox()
   #    fb.div('1) numberTextbox - places non specificato')
   #    for i in range(5):
   #        fb.numberTextbox(places=i)
   #        fb.div('%s) numberTextbox - places = %s' % (i+2,i))