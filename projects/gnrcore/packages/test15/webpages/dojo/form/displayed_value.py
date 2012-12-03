# -*- coding: UTF-8 -*-

"""Displayed value"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_source=True
    
    def test_1_dateTextBox(self, pane):
        """DateTextBox"""
        fb=pane.formbuilder(cols=2)
        #fb.datetextbox(lbl='No constraints',value='^.date_1',popup=False)
        #fb.div('^.date_1',mask='Masked value:%s')
        fb.datetextbox(lbl='Full',value='^.date_2',popup=False,
                format='full')
        fb.div('^.tttt',format='short',dtype='DH')
        fb.button('Test',fire='.newdate')
        fb.dataController('SET .tttt = new Date();',_fired='^.newdate')
        #fb.div('^.date_2',mask='Masked value:%s',format='short')
        
    def test_2_numberTextBox(self, pane):
        """NumberTextBox"""
        fb=pane.formbuilder(cols=2)
        fb.numberTextBox(lbl='No constraints',value='^.number_1')
        fb.div('^.number_1',format='##0.00000',mask='Masked value:%s')


    def test_5_textbox_regex(self,pane):
        fb=pane.formbuilder(cols=2)
        tb = fb.textbox(lbl='Address',value='^.address',validate_regex='![?]{2,2}')


    def test_4_textbox_phone(self,pane):
        """NumberTextBox"""
        fb=pane.formbuilder(cols=2)
        fb.textbox(lbl='Phone',value='^.phone_1',format='### ### #',validate_len='3:8',
                    validate_len_max='!!Too long',validate_len_min='!!Too short')
        fb.textbox(lbl='Phone 2',value='^.phone_2',format='(##)### ### #',displayFormattedValue=True)
        fb.textbox(lbl='Phone 3',value='^.phone_3',format='(##)## ## #')

       # tb.span('^.phone_1?_formattedValue',_attachPoint='focusNode.parentNode',_class='genroFormattedSpan')

    def test_3_comboBox(self, pane):
        """ComboBox"""
        fb=pane.formbuilder(cols=2)
        fb.comboBox(lbl='Autocomplete=False',value='^.combo_1',autocomplete=False,values='Foo,Bar,Baz,Egg,Spam boy')
        fb.div('^.combo_1',mask='Masked value:%s')
        fb.comboBox(lbl='Autocomplete=True',value='^.combo_2',autocomplete=True,values='Foo,Bar,Baz,Egg,Spam boy')
        fb.div('^.combo_2',mask='Masked value:%s')


    def test_6_filteringSelect(self, pane):
        """ComboBox"""
        fb=pane.formbuilder(cols=2)
        fb.filteringSelect(lbl='Filtering',value='^.filtering',values='pippo:Pippo,pluto:Pluto,paperino:Paperino')
        fb.div('^.filtering?_displayedValue')

