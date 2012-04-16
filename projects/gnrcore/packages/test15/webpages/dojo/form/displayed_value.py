# -*- coding: UTF-8 -*-

"""Displayed value"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_source=True
    
    def test_1_dateTextBox(self, pane):
        """DateTextBox"""
        fb=pane.formbuilder(cols=2)
        fb.datetextbox(lbl='No constraints',value='^.date_1',popup=False)
        fb.div('^.date_1',mask='Masked value:%s')
        fb.datetextbox(lbl='Constraints',value='^.date_1',popup=False,
                formatLength='full')
        fb.div('^.date_1',mask='Masked value:%s')
        
    def test_2_numberTextBox(self, pane):
        """NumberTextBox"""
        fb=pane.formbuilder(cols=2)
        fb.numberTextBox(lbl='No constraints',value='^.number_1')
        fb.div('^.number_1',format='##0.00000',mask='Masked value:%s')
        
    def test_3_comboBox(self, pane):
        """ComboBox"""
        fb=pane.formbuilder(cols=2)
        fb.comboBox(lbl='Autocomplete=False',value='^.combo_1',autocomplete=False,values='Foo,Bar,Baz,Egg,Spam boy')
        fb.div('^.combo_1',mask='Masked value:%s')
        fb.comboBox(lbl='Autocomplete=True',value='^.combo_2',autocomplete=True,values='Foo,Bar,Baz,Egg,Spam boy')
        fb.div('^.combo_2',mask='Masked value:%s')
