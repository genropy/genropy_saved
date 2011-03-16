.. _genro_validations:

===========
validations
===========
    
    add??? parlare della form, e quindi dire che le validazioni rendono vere o false le form (cioè, se anche un solo
    valore ha una validazione sbagliata, la form non è valida)
    
    With Genro you can use a system of javascript validations: they allow to control the user entries, sending
    a tooltip warning for the uncorrect typing. In a webpage for database table management, if any of the
    validation is not satisfied, users can't save the actual record on which they are writing until the wrong
    insertions are corrected.
    
    add??? list of validations:

.. validationTags: ['dbselect','notnull','empty','case','len','email','regex','call','nodup','exist','remote'],
    
    A form is a method to manage both data loading and data saving.
    
    Every form is characterized by a formId (MANDATORY) and by a datapath (MANDATORY):
    with formId you can interact with the code, while with datapath you can link every object you want
    to the form itself.
    Pay attention that only the data linked to form's datapath are managed by the form (for more details
    see "datapath")
    
    Every form is characterized by a "load" action and a "save" action: every time user wants to create
    a new record (generally for his database) Genro make a "load": this action allows to reload a "form"
    in its standard form. Until the form isn't completely loaded, the program prevents the user to perform
    any writing action (the syntax is "genro.formById(f_id).loaded()", where f_id is the formId)
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
