# -*- coding: UTF-8 -*-

"""Radio Button Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height=350,description='Simple vertical slider')
    def slider1(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.div('The slider and the numerical field are linked: change one of them to change them all', colspan=2)
        fb.verticalSlider(value='^.number', height='100px')
        fb.numberTextbox(value='^.number', lbl='height')
    def doc_slider1(self):
        """A slider widget sets the value of the datastore path"""



    @example(code=2,height=350,description='Simple horizontal slider')
    def slider2(self, pane):
        fb = pane.formbuilder(cols=4)
        pane.data('test2.decimals', '2')
        fb.horizontalSlider(value='^.integer_number', width='200px', maximum=50,
                            discreteValues=51, lbl='!!Integer number')
        fb.numberTextBox(value='^.integer_number', width='11em', colspan=2, readOnly=True)
        fb.div("""With "discreteValues", "minimum" and "maximum" attributes you can allow to
                  write only integer numbers.""")

        fb.horizontalSlider(value='^.float_number', width='200px', minimum=10, lbl='!!Float number')
        fb.numberTextBox(value='^.float_number', width='11em', places='^.decimals', readOnly=True)
        fb.numberSpinner(value='^.decimals', width='4em', min=0, max=15, lbl='decimals')
        fb.div("""Here you can choose the number of decimals.""")

    def doc_slider2(self):
        """A slider widget sets the value of the datastore path"""



    @example(code=3,height=350,description='widthness')
    def slider3(self, pane):
        pane = pane.contentPane(height='400px')
        pane.data('.icon', 'icnBaseOk')
        pane.data('.fontfam', 'Courier')
        pane.data('.font', 9)
        pane.dataFormula('.font_size', 'font+umf', font='^.font', umf='^.um_font')
        
        fb = pane.formbuilder(cols=5, fld_width='6em')
        fb.horizontalslider(value='^.font', minimum=4, maximum=120, width='20em',
                            discreteValues=117, intermediateChanges=True, lbl='!!Width font')
        fb.numberTextBox(value='^.font', readOnly=True)
        fb.comboBox(value='^.um_font', values='pt,px', default='pt')
        fb.filteringSelect(value='^.fontfam', lbl='Font',
                           values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
        fb.filteringSelect(value='^.icon', lbl='icon',
                           values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')
        
        fb = pane.formbuilder()
        fb.button('Save it', action="alert('Saving!')", iconClass='^.icon',
                             font_size='^.font_size', font_family='^.fontfam')

    def doc_slider3(self):
        """This example shows a lot of tools to achieve the result, the first being the slider"""
