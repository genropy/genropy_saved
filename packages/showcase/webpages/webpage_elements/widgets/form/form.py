# -*- coding: UTF-8 -*-

# form.py
# Created by Filippo Astolfi on 2010-09-13.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Form"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    """A form is a method to manage both data loading and data saving.
    
    Every form is characterized by a formId (MANDATORY) and by a datapath (MANDATORY):
    with formId you can interact with the code, while with datapath you can link every object you want
    to the form itself.
    Pay attention that only the data linked to form's datapath are managed by the form (for more details
    see "datapath")
    
    Every form is characterized by a "load" action and a "save" action: every time user wants to create
    a new record (generally for his database) Genro make a "load": this action allows to reload a "form"
    in its standard form. Until the form isn't completely loaded, the program prevents the user to perform
    any writing action (the sintax is "genro.formById(f_id).loaded()", where f_id is the formId)
    When the load is over, Genro makes user able to write. With the button "save" the program allows user
    to save his progress. Performing the "save" action, Genro completely reload the standard form.
    
    For helping user not to make some mistakes in compiling the form, Genro provides an helpful developer's tool:
    the validations. With validations you can force an user to perform an action, without which he can't
    save his written data.
    
    Let's see validations in details:
    - validate_notnull:
        validate_notnull=True,                      --> Set field as a required field
        validate_notnull_error='!!Hint tooltip'     --> Set a red border to field until is filled from user,
                                                        with a hint tooltip appearing on mouse click.
    - validate_len:
        validate_len='NUMBER:NUMBER'                --> Minimum and maximum value of characters
        
    - validate_onReject:
        validate_onReject='alert(" ")'  --> alert window (rejected writing user)
        
    - validate_onAccept:
        validate_onAccept='alert(" ")'  --> alert window (confirmed writing user)
        
    - validate_email:
        validate_email=True             --> validate an e-mail format.
        
    - validate_case (this is not a real validation, but...???):
        validate_case='c'   --> 'Capitalize', set first letter of every word uppercase
        validate_case='u'   --> 'Uppercase', set every letter of every word uppercase
        validate_case='l'   --> 'Lowercase', set every letter of every word lowcase
    
    - The controller path:
    Another useful tool is the controller path; we suggest you to create it, but if you don't
    it will be created automatically in the following path: ???
    In the controller path lies control informations; if you want to check it, just click "CTRL+SHIFT+D"
    to open dataSource, so you can view all controller path's informations.
    Let's check out these informations:
        - loading: ???
        - invalidFields: this address contains all wrong fields compiled from user.
        - valid: this address report "true" if there aren't invalid fields,
                 "false" if there is one invalid field (or more).
        - changesLogger: tracks the story-line of user changes.
        - changed: "true" if user compiles some part of the form, "false" if there is no changes.
                   If this parameter is "false" and user tries to save the form, Genro prevents to
                   save the form warning user with an alert message reporting: "nochange".
        - is_newrecord: ???undefined
        - loaded: it s "true" when a new form is loaded.
        - saving: this folder is created during the save. ???cosa_si_trova_dentro?
        - saved: this folder is created after the save. ???cosa_si_trova_dentro?
        - save_failed: report the same alert message reported to user:
            "nochange" if user tries to save without making any changement.
            "invalid" if user doesn't meet all the form requirements.
            This folder is created on a failed save.
    
    When you save the form, a message will show you the contents of your save; it should be like this one:
    <?xml version="1.0" encoding="utf-8"?>
    <GenRoBag>
    <name _loadedValue="::NN">Mario</name>
    <surname _T="NN"/>
    </GenRoBag> 
    
    So the form will be saved into a GenRoBag (XML type), every row is composed by a single form field, with
    the following sintax:
        <field_name _loadedValue="::NN">record_value</field_name>
    """

    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to form.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       borderContainer     --> webpages/widgets/layout/border.py
    #       button              --> button.py
    #       contentPane         --> webpages/widgets/layout/border.py
    #       formbuilder         --> formbuilder.py
    #       textbox             --> textbox.py

    def test_1_basicForm(self, pane):
        """Basic Form"""
        bc = pane.borderContainer(height='250px', datapath='test1')
        formpane = self._formpane(bc, datapath='test1', formId='test1', loader='basic')
        fb = formpane.formbuilder(border_spacing='3px')
        fb.div("""In this basic example we let you test a simple case of form.""",
               font_size='.9em', text_align='justify')
        fb.div("""We present you two fields (name and surname) and in the right we'll show you a "load"
        button, a "save" button and what you'll normally get in dataSource.""",
               font_size='.9em', text_align='justify')
        fb.div("""1) Try to save WITHOUT doing any change. An alert message we'll warn you that you can't
        save because you have not made any change.""",
               font_size='.9em', text_align='justify')
        fb.div("""2) Now try to write something in the form (in the name field, in the surname field or
        in both); after that, try to save. A message will show you that your data has been saved in a GenRoBag.
        After that, if you try to save again you will hear a sound noise; this sound indicates that you CAN'T
        save again, even if you change something in the form, UNLESS you click the "load" button. This is a
        way to prevent to rewrite on a save data.)""",
               font_size='.9em', text_align='justify', margin_bottom='10px')
        fb.textbox(value='^.name', lbl='!!Name')
        fb.textbox(value='^.surname', lbl='!!Surname')

    def test_2_validations(self, pane):
        """Validations"""
        bc = pane.borderContainer(height='350px', datapath='test2')
        formpane = self._formpane(bc, datapath='test2', formId='test2', loader='basic')
        fb = formpane.formbuilder(cols=2, border_spacing='3px')
        fb.div("""In this example we let you test validations.""",
               colspan=2, font_size='.9em', text_align='justify')
        fb.div("""1) If you try to save BEFORE doing anything else, you will notice the same behavior
               of test1 (that is an alert message reporting "nochange" and the impossibility to save your
               form).""",
               colspan=2, font_size='.9em', text_align='justify')
        fb.div("""2) Now, compile any field EXCEPT for "Address" field. After that, try to save.
               An alert message reporting "invalid" will warn you that you can't save because you haven't
               written in the mandatory fields.""",
               colspan=2, font_size='.9em', text_align='justify')
        fb.div("""3) You can save if you have almost compiled mandatory fields, so try to write in the
               "Address" field.""",
               colspan=2, font_size='.9em', text_align='justify')
        fb.div("""4) If you write in the last three fields (labeled as "Fiscal code", "Job" or "e-mail")
               you have to meet the demands of those fields; if you don't and try to save, an alert message
               ("invalid") will warn you that you can't save the form.""",
               colspan=2, font_size='.9em', text_align='justify', margin_bottom='10px')
        fb.textbox(value='^.name', lbl='!!Name', validate_case='c')
        fb.div('Capitalize field',
               font_size='.9em', text_align='justify')
        fb.textbox(value='^.surname', lbl='!!Surname', validate_case='u')
        fb.div('Uppercase field',
               font_size='.9em', text_align='justify')
        fb.textbox(value='^.profession', lbl='!!Profession', validate_case='l')
        fb.div('Lowercase field',
               font_size='.9em', text_align='justify')
        fb.textbox(value='^.address', lbl='!!Address',
                   validate_notnull=True,
                   validate_notnull_error='!!Required field')
        fb.div('Not null field',
               font_size='.9em', text_align='justify')
        fb.textbox(value='^.fiscal_code', lbl='!!Fiscal code', validate_len='3:10')
        fb.div('Precise lenght field [3:10]',
               font_size='.9em', text_align='justify')
        fb.textBox(value='^.job', lbl='!!Job',
                   validate_len='6:',
                   validate_onReject='alert("The name "+"\'"+value+"\'"+" is too short")')
        fb.div('Insert 6 or more characters (try to write less than six characters!)',
               font_size='.9em', text_align='justify')
        fb.textBox(value='^.email_2', lbl="e-mail",
                   validate_email=True)
        fb.div('required e-mail correct form',
               font_size='.9em', text_align='justify')

    def test_3_prova(self, pane):
        """Genro and Dojo validations"""
        bc = pane.borderContainer(height='350px', datapath='test3')
        formpane = self._formpane(bc, datapath='test3', formId='test3', loader='basic')
        tc = pane.tabContainer(datapath='test3', formId='testform')
        self.genroValidation(tc)
        tc2 = tc.tabContainer(title='Dojo Validation')
        self.numberTextbox(tc2)
        self.currencyTextbox(tc2)
        self.dateTextbox(tc2)
        self.timeTextbox(tc2)
        self.textArea(tc2)

    def _formpane(self, bc, datapath=None, formId=None, loader=None):
        right = bc.contentPane(region='right', width='200px', splitter=True)
        center = bc.contentPane(region='center', formId=formId, datapath='.data', controllerPath='%s.form' % datapath)
        right.button('Load', fire='.load')
        right.button('Save', action='genro.formById(f_id).save()', f_id=formId)
        right.div(height='200px', overflow='auto').tree(storepath=datapath)
        if loader == 'basic':
            bc.dataController("genro.formById(f_id).load()", _fired="^.load", _onStart=True, f_id=formId)
            bc.dataController("SET .data= new gnr.GnrBag(); genro.formById(f_id).loaded();",
                              nodeId="%s_loader" % formId, f_id=formId) #fire node
            bc.dataController("alert(saved_data.toXml()); genro.formById(f_id).saved();", nodeId="%s_saver" % formId,
                              saved_data='=.data', f_id=formId) #fire node
            bc.dataController("alert(msg)", msg="^.form.save_failed")

        return center

    def genroValidation(self, tc):
        tc.dataController("""var bag = new gnr.GnrBag();
                            bag.setItem('name','pippo');
                            bag.setItem('notnull',true);
                            bag.setItem('iswarning',true);
                            bag.setItem('len','2:4');
                            bag.setItem('case','upper');
                            bag.setItem('min',10);
                            bag.setItem('max',100);
                            SET test.textBox=bag;""", nodeId='testform_loader')
        tc.dataController("var result = GET test;alert(result.toXml());", nodeId='testform_saver')
        fb = tc.contentPane(title='Genro Validation', datapath='.textBox').formbuilder(cols=2, border_spacing='10px')
        tc.dataController('genro.formById("testform").load({sync:true});', _fired='^test.doload')
        fb.div('The boxes with (*) have a tooltip for helping code comprehension', colspan=2)
        fb.button('Load', fire='^test.doload')
        fb.button('Save', action='genro.formById("testform").save()', disabled='== !(_changed && _valid)',
                  _changed='^gnr.forms.testform.changed', _valid='^gnr.forms.testform.valid')

        fb.button('Set Value', action='SET .name="John"', colspan=2)
        fb.textBox(value='^.len', tooltip='Here you define the size of \'Name(Len)\' textbox. (Format --> 4:7)',
                   lbl="Len (*)")
        fb.textBox(value='^.name4', validate_len='^.len',
                   validate_len_min='alert("too much short!")', validate_len_max='alert("too much long!")',
                   lbl="Name (Len)")
        #    fb.textBox(value='^.case',colspan=2,lbl="Set case validation")
        fb.textBox(value='^.name', validate_len='4:', tooltip='Insert 4 or more characters',
                   validate_onReject='alert("The name "+"\'"+value+"\'"+" is too short")',
                   validate_onAccept='alert("correct lenght of "+"\'"+value+"\'")', lbl="Name (*)")
        fb.textBox(value='^.name', lbl="Name echo")
        fb.textBox(value='^.nameup', validate_case='upper', lbl="Name up")
        fb.textBox(value='^.namelow', validate_case='lower', lbl="Name low")
        fb.textBox(value='^.namecap', validate_case='capitalize', lbl="Name capitalized")
        #    fb.checkbox(value='^.notnull',lbl="notnull")
        #    fb.textBox(value='^.namenotrim',trim=False,validate_notnull='^.notnull',
        #               validate_notnull_error='required!',lbl="Name notrim notnull")
        fb.textBox(value='^.email', validate_email=True, lbl="Email")
        fb.textBox(value='^.nameregex', validate_regex='abc', validate_regex_iswarning='^.iswarning',
                   lbl="contains abc")
        fb.checkbox(value='^.iswarning', lbl="iswarning (*)", tooltip="""if selected, the tooltip in box labelled \'contains
                                                                       abc\' is \'warning\'; else you get error""")
        fb.span('Validation using Callback and Remote function', colspan=2, color='== _email ? "red" : "green"',
                _email='^.email')

        fb.numberTextBox(value='^.min', lbl="Min")
        fb.numberTextBox(value='^.max', lbl="Max")
        fb.numberTextBox(value='^.minmax', lbl="between min and max",
                         validate_min='^.min', validate_max='^.max',
                         validate_call="""
                                       if (value < min){
                                           return 'the value inserted is too small';
                                       } else if (value > max){
                                           return 'the value inserted is too large';
                                       }""")
        fb.textBox(value='^.remote', validate_remote="nameremote", validate_name='^.name',
                   validate_remote_error='different from name field\'s value inserted',
                   tooltip='for validation, insert the same words of box labelled \'Name\'', lbl='remote Name (*)')

    def rpc_nameremote(self, value=None, name=None, **kwargs):
        if not value:
            return
        if value.lower() == name.lower():
            result = Bag()
            result['value'] = value.upper()
            return result
        else:
            return 'remote'

    def numberTextbox(self, tc):
        fb = tc.contentPane(title='numberTextbox', datapath='.numberTextbox').formbuilder(cols=2, border_spacing='10px')
        fb.numberTextbox(value='^.age', lbl="Age", default=36)
        fb.numberTextbox(value='^.age', lbl="Age echo")

    def currencyTextbox(self, tc):
        fb = tc.contentPane(title='currencyTextbox', datapath='.currencyTextbox').formbuilder(cols=2,
                                                                                              border_spacing='10px')
        fb.currencyTextbox(value='^.amount', default=1123.34, currency='EUR', locale='it', lbl="Age")
        fb.currencyTextbox(value='^.amount', currency='EUR', locale='it', lbl="Age echo")

    def dateTextbox(self, tc):
        fb = tc.contentPane(title='dateTextbox', datapath='.dateTextbox').formbuilder(cols=2, border_spacing='10px')
        fb.dateTextbox(value='^.birthday', lbl='Birthday')
        fb.dateTextbox(value='^.birthday', lbl='Birthday echo')

    def timeTextbox(self, tc):
        fb = tc.contentPane(title='timeTextbox', datapath='.timeTextbox').formbuilder(cols=2, border_spacing='10px')
        fb.timeTextbox(value='^.meetingAt', lbl='Meeting Time')
        fb.timeTextbox(value='^.meetingAt', lbl='Meeting Time echo')

    def textArea(self, tc):
        fb = tc.contentPane(title='textArea', datapath='.textArea').formbuilder(cols=2, border_spacing='10px')
        fb.textArea(value='^.remarks', lbl='Remarks')
        fb.textArea(value='^.remarks', lbl='Remarks echo')
          