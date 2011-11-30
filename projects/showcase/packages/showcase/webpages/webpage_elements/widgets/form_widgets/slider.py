# -*- coding: UTF-8 -*-
"""Slider"""

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_simple(self, pane):
        """Simple vertical slider"""
        fb = pane.formbuilder(cols=2)
        fb.div('The slider and the numerical field are linked: change one of them to change them all', colspan=2)
        fb.verticalSlider(value='^.number', height='100px')
        fb.numberTextbox(value='^.number', lbl='height')
        
    def test_2_simple(self, pane):
        """Simple horizontal slider"""
        fb = pane.formbuilder(datapath='test2', cols=4)
        pane.data('test2.decimals', '2')
        fb.horizontalSlider(value='^.integer_number', width='200px', maximum=50,
                            discreteValues=51, lbl='!!Integer number')
        fb.numberTextBox(value='^.integer_number', width='4em', colspan=2,
                         validate_remote=self.check_number(num),
                         validate_remote_error='Error!')
        fb.div("""With "discreteValues", "minimum" and "maximum" attributes you can allow to
                  write only integer numbers.""",
               font_size='.9em', text_align='justify')
               
        fb.horizontalSlider(value='^.float_number', width='200px', minimum=10, lbl='!!Float number')
        fb.numberTextBox(value='^.float_number', width='4em', places='^.decimals')
        fb.numberSpinner(value='^.decimals', width='4em', min=0, max=15, lbl='decimals')
        fb.div("""Here you can choose the number of decimals.""",
               font_size='.9em', text_align='justify')
               
    def check_number(self, num, **kwargs):
        return 'hello'
        
    def test_3_hslider(self, pane):
        """Horizontal slider"""
        fb = pane.formbuilder(datapath='test3', cols=4)
        fb.data('.icon', 'icnBaseOk')
        fb.data('.fontfam', 'Courier')
        fb.dataFormula('.width_calc', 'w+umw', w='^.width', umw='^.um_width')
        fb.dataFormula('.font_size', 'font+umf', font='^.font', umf='^.um_font')
        
        fb.horizontalSlider(value='^.width', width='200px', minimum=3,
                            intermediateChanges=True, lbl='!!Width button')
        fb.numberTextBox(value='^.width', width='4em')
        fb.comboBox(value='^.um_width', width='5em', values='em,px,%', default='em')
        fb.br()
        
        fb.horizontalslider(value='^.font', width='200px', minimum=4,
                            discreteValues=97, intermediateChanges=True, lbl='!!Width font')
        fb.numberTextBox(value='^.font', width='4em')
        fb.comboBox(value='^.um_font', width='5em', values='pt,px', default='pt')
        fb.filteringSelect(value='^.fontfam', width='8em', lbl='Font',
                           values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
        fb.filteringSelect(value='^.icon', width='5em', colspan=4, lbl='icon',
                           values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')
        fb.button('Save it', action="alert('Saving!')", tooltip='click me', colspan=4,
                  ffont_size='^.font_size', font_family='^.fontfam',
                  iconClass='^.icon', width='^.width_calc')