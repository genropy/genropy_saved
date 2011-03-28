.. _genro_validations:

===========
validations
===========
    
    * :ref:`validations_def`
    * :ref:`validations_list`
    * :ref:`validations_example`: :ref:`validations_form_example`

.. _validations_def:

Definition
==========

    To make obligations onto user input filling out a :ref:`genro_form_index`,
    Genro provides an helpful developer's tool: the validations.
    
    The validations are able to decide whether a form (or a single element, like a
    :ref:`genro_form_widgets_index`) is correct or uncorrect.
    
    In Genro you can use a system of javascript validations: they allow to control
    the user entries, sending a tooltip warning for the uncorrect typing. In a
    webpage for database table management, if any of the validation is not satisfied,
    users can't save the actual record on which they are writing until the wrong
    insertions are corrected.
    
.. _validations_list:

Validations list
================

    Let's see a complete list of Genro validations:
    
    * :ref:`genro_validate_call`
    * :ref:`genro_validate_case`
    * :ref:`genro_validate_dbselect`
    * :ref:`genro_validate_email`
    * :ref:`genro_validate_empty`
    * :ref:`genro_validate_exist`
    * :ref:`genro_validate_gridnodup`
    * :ref:`genro_validate_len`
    * :ref:`genro_validate_nodup`
    * :ref:`genro_validate_notnull`
    * :ref:`genro_validate_regex`
    * :ref:`genro_validate_remote`
    
.. _genro_validate_call:

validate_call
-------------

    add???
    
.. _genro_validate_case:

validate_case
-------------

    add???
    
.. _genro_validate_dbselect:

validate_dbselect
-----------------

    add???
    
.. _genro_validate_email:

validate_email
--------------

    add???
    
.. _genro_validate_empty:

validate_empty
--------------

    add???
    
.. _genro_validate_exist:

validate_exist
--------------

    add???
    
.. _genro_validate_gridnodup:

validate_gridnodup
------------------

    add???
    
.. _genro_validate_len:

validate_len
------------

    add???
    
.. _genro_validate_nodup:

validate_nodup
--------------

    add???
    
.. _genro_validate_notnull:

validate_notnull
----------------

    add???
    
.. _genro_validate_regex:

validate_regex
--------------

    add???
    
.. _genro_validate_remote:

validate_remote
---------------

    add???
    
    
    validationTags: ['dbselect','notnull','empty','case','len','email','regex','call','nodup','exist','remote'],
    
    Let's see validations in details:
    
    * validate_notnull:
    
        * validate_notnull=True,                    --> Set field as a required field
        * validate_notnull_error='Hint tooltip'     --> Set a hint tooltip appearing on mouse click for user uncorrect input
    * validate_len:
        validate_len='NUMBER:NUMBER'                --> Minimum and maximum values for field's lenght
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
    
.. _validations_example:

Examples
========

.. _validations_form_example:

form example
------------

    class GnrCustomWebPage(object):
        def main(self,root,**kwargs):
            fb = root.formbuilder(cols=2)
            fb.textbox(value='^.name',lbl='Name', validate_case='c')
            fb.div('Capitalized field')
            fb.textbox(value='^.surname',lbl='Surname', validate_case='c')
            fb.div('Capitalized field')
            fb.textbox(value='^.job',lbl='Profession',
                       validate_case='l',
                       validate_notnull=True,validate_notnull_error='!!Required field')
            fb.div('Not null field; lowercase field')
            fb.textbox(value='^.address', lbl='!!Address')
            fb.div('No validation is required')
            fb.textbox(value='^.fiscal_code',lbl='!!Fiscal code',
                       validate_len='16',validate_case='u')
            fb.div('Uppercased field; Precise length field [16]')
            fb.textBox(value='^.long',lbl='Long string',validate_len='6:',
                       validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
            fb.div('Insert 6 or more characters (wrong input notification)')
            fb.textBox(value='^.email', lbl="email", validate_email=True,
                       validate_onAccept='alert("Correct email format")',
                       validate_notnull=True)
            fb.div('required correct e-mail form (correct input notification)')
            