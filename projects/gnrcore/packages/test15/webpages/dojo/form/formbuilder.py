# -*- coding: UTF-8 -*-

"""Formbuilder"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'tundra'
    
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
        
