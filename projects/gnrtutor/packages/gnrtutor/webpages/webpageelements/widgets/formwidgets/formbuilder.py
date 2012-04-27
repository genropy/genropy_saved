# -*- coding: UTF-8 -*-

"""Formbuilder"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"    


    @example(code=1,height=300,description='Basic formbuilder')
    def formbuilder1(self, pane):
        fb = pane.formbuilder(cols=2)
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.numberTextbox(value='^.age', lbl="Age")
        fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
        fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
        fb.textbox(value='^.job.profession', lbl='Job')
        fb.textbox(value='^.job.company_name', lbl='Company name')
    
    def doc_formbuilder1(self):
        """ blah"""

    @example(code=2,height=400,description="Basic formbuilder with 'lbl' and 'label' attributes")
    def formbuilder2(self, pane):
        fb = pane.formbuilder(datapath='.lbl', cols=2, lbl_width='5em')
        fb.div('The next fields have the \"lbl\" attribute:', colspan=2)
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.textbox(value='^.job', lbl='Profession')
        fb.numberTextbox(value='^.age', lbl='Age')
        fb = pane.formbuilder(datapath='.label', cols=2, margin_left='5em')
        fb.div('The next fields have the \"label\" attribute:', colspan=2)
        fb.div('Favorite sport:')
        fb.div('Favorite browser:')
        fb.checkbox(value='^.checkbox.football',label='Football')
        fb.radiobutton(label='Internet explorer',value='^.radio.IE',group='genre1')
        fb.checkbox(value='^.checkbox.basketball',label='Basketball')
        fb.radiobutton('Mozilla Firefox',value='^.radio.firefox',group='genre1')
        fb.checkbox(value='^.checkbox.tennis',label='Tennis')
        fb.radiobutton('Google Chrome',value='^.radio.chrome',group='genre1')

    def doc_formbuilder2(self):
        """ blah"""

    @example(code=3,height=400,description="We introduce here the most common attributes of the formbuilder")
    def formbuilder3(self, pane):
        pane.div("""fb = pane.formbuilder(cols=2, lbl_width=\'8em\',fld_width=\'15em\', lbl_color=\'teal\')""", margin_left='6em')
        fb = pane.formbuilder(cols=2, lbl_width='6em', fld_width='15em', lbl_color='gray')
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.numberTextbox(value='^.age', lbl="Age")
        fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
        fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
        fb.textbox(value='^.job.profession', lbl='Job')
        fb.textbox(value='^.job.company_name', lbl='Company name')
        fb.dbSelect(dbtable='showcase.person', value='^.artist', lbl='Favorite artist', hasDownArrow=True)

    def doc_formbuilder3(self):
        """ blah"""