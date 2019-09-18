#!/usr/bin/python
# -*- coding: utf-8 -*-

"genro.dom.centerOn"

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    
    def test_0_hidden(self, pane):
        fb = pane.formbuilder(cols=2,spacing=10)
        fb.data('^.hidden_alfa',True)
        fb.checkbox(value='^.hidden_alfa',label='Hidden alfa')
        fb.checkbox(value='^.hidden_beta',label='Hidden beta')
        fb.textbox(value='^.zzzz',lbl='zzz',colspan=2)

        fb.textbox(value='^.alfa',lbl='Alfa',hidden='^.hidden_alfa')
        fb.checkboxText(value='^.beta',lbl='Beta',hidden='^.hidden_beta',values='pippo,pluto,paperino,/,pancrazio')
        fb.textbox(value='^.yyy',lbl='yyy',colspan=2)
        fb.checkbox(value='^.hidden_gamma',label='Hidden gamma')
        fb.checkbox(value='^.row_hidden',label='Row hidden',hidden='^.hidden_gamma',zzz='^.yyy')
        fb.textbox(value='^.uuu',lbl='UUU')

        fb.textbox(value='^.r1',lbl='R1',row_hidden='^.row_hidden')        
        fb.textbox(value='^.r1',lbl='R2')


    
    def test_1_hidden_group(self, pane):
        fb = pane.formbuilder(cols=2,spacing=10)
        fb.data('^.hidden_alfa',True)
        fb.checkbox(value='^.hidden_alfa',label='Hidden alfa')
        fb.checkbox(value='^.hidden_beta',label='Hidden beta')
        fb.textbox(value='^.zzzz',lbl='zzz',colspan=2)

        fb.textbox(value='^.alfa',lbl='Alfa',hidden='^.hidden_alfa',hiddenGroup='alfa')
        fb.textbox(value='^.beta',lbl='Beta')
        fb.textbox(value='^.yyy',lbl='yyy',colspan=2,hiddenGroup='alfa')
        fb.checkbox(value='^.hidden_gamma',label='Hidden gamma')
        fb.checkbox(value='^.row_hidden',label='Row hidden')
        fb.textbox(value='^.uuu',lbl='UUU')

        fb.textbox(value='^.r1',lbl='R1',hiddenGroup='alfa')        
        fb.textbox(value='^.r1',lbl='R2')

    def test_2_nofb(self, pane):
        pane.textbox('^.status',lbl='Status')
        pane.br()
        pane.button('Test',action='alert("test")',hidden='^.status?=#v!="SHOW"')
        pane.checkbox(value='^.zio',hidden='^.status?=#v=="SHOW"',label='Not SHOW')

    def test_3_cbtext(self,pane):
        fb = pane.formbuilder(cols=2,spacing=10)
        fb.data('.hidden_beta',True)
        fb.checkbox(value='^.hidden_beta',label='Hidden beta')
        fb.br()
        fb.checkboxText(value='^.beta',lbl='Beta',hidden='^.hidden_beta',
                    values='/2,pippo,pluto,paperino,pancrazio',
                    popup=True)
        fb.textbox(value='^.beta',lbl='Valori')
