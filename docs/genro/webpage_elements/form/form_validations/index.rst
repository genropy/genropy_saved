.. _genro_validations:

===========
validations
===========
    
    To help users not to make mistakes in compiling a :ref:`genro_form_index`, Genro provides
    an helpful developer's tool: the validations.
    
    The validations are able to decide whether a form (or a single element, like a
    :ref:`genro_form_widgets_index`) is correct or uncorrect.
    
    In Genro you can use a system of javascript validations: they allow to control the user
    entries, sending a tooltip warning for the uncorrect typing. In a webpage for database
    table management, if any of the validation is not satisfied, users can't save the actual
    record on which they are writing until the wrong insertions are corrected.
    
    Let see a complete list of Genro validations:
    
    validationTags: ['dbselect','notnull','empty','case','len','email','regex','call','nodup','exist','remote'],
    
    Let's see validations in details:
    
    * validate_notnull:
        validate_notnull=True,                      --> Set field as a required field
        validate_notnull_error='!!Hint tooltip'     --> Set a red border to field until is filled from user,
                                                        with a hint tooltip appearing on mouse click.
    * validate_len:
        validate_len='NUMBER:NUMBER'                --> Minimum and maximum value of characters
    * validate_onReject:
        validate_onReject='alert(" ")'  --> alert window (rejected writing user)
    * validate_onAccept:
        validate_onAccept='alert(" ")'  --> alert window (confirmed writing user)
    * validate_email:
        validate_email=True             --> validate an e-mail format.
    * validate_case
        validate_case='c'   --> 'Capitalize', set first letter of every word uppercase
        validate_case='u'   --> 'Uppercase', set every letter of every word uppercase
        validate_case='l'   --> 'Lowercase', set every letter of every word lowcase