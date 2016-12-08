# -*- coding: UTF-8 -*-

"""Formbuilder"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'tundra'
    
    def test_0_htmltable(self, pane):
        t = pane.table(style='border-collapse:collapse',border='1px solid silver').tbody()
        r = t.tr()
        r.td(width='100%')
        r.td(width='50%').div('Pippo')
        r.td(width='50%').div('Pluto')

        fb = pane.formbuilder(cols=2,border_spacing='3px',border='1px solid silver',colswidth='auto')
        fb.div('Pippo',lbl='AAlfa')
        fb.div('Pluto',lbl='Beta')

    def test_1_basic(self, pane):
        """Basic formbuilder"""
        fb = pane.formbuilder(cols=2, border_spacing='3px', width='100%', fld_width='30px')
        fb.textbox(value='^.aaa', lbl='aaa', width='100%')
        fb.data('.bb','piero')
        fb.textbox(value='^.bb', lbl='bb',readOnly=True)
        fb.textbox(value='^.cc', lbl='cc', width='100%', colspan=2)
        
        b = Bag()
        b.setItem('foo',None,id='foo',caption='Foo',test='AAA')
        b.setItem('bar',None,id='bar',caption='Bar',test='BBB')
        b.setItem('spam',None,id='spam',caption='Spam',test='CCC')
        
        fb.data('.xxx',b)
        fb.combobox(value='^.ttt',lbl='ttt',width='10em',storepath='.xxx',selected_test='.zzz')
        fb.div('^.zzz')
        
    def test_2_tabindex(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.textbox(value='^.val_1',lbl='Val 1',tabindex=1)
        fb.textbox(value='^.val_3',lbl='Val 3',tabindex=3)
        fb.textbox(value='^.val_2',lbl='Val 2',tabindex=2)
        fb.textbox(value='^.val_4',lbl='Val 4',tabindex=4)


    def test_3_tabindex(self, pane):
        fb = pane.formbuilder(cols=4,byColumn=True)
        fb.textbox(value='^.val_1',lbl='Val 1')
        fb.textbox(value='^.val_3',lbl='Val 3')
        fb.textbox(value='^.val_2',lbl='Val 2')
        fb.textbox(value='^.val_4',lbl='Val 4')
        fb.textbox(value='^.val_5',lbl='Val 5')
        fb.textbox(value='^.val_7',lbl='Val 7')
        fb.textbox(value='^.val_6',lbl='Val 6')
        fb.textbox(value='^.val_8',lbl='Val 8')
