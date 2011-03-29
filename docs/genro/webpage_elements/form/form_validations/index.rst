.. _genro_validations:

===========
validations
===========
    
    * :ref:`validations_def`
    * :ref:`validations_list`
    * :ref:`validations_other_list`
    * :ref:`validations_common`
    * :ref:`validations_example`: :ref:`validations_form_example`

.. _validations_def:

definition
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
    
    For every validation, you have a list of :ref:`validations_common` through which
    you can modify the standard validation features.
    
.. _validations_list:

validations list
================

    Let's see a complete list of Genro validations:
    
    * *validate_call*: add???
    * *validate_dbselect*: used in the :ref:`genro_dbselect` form widget.
      If ``True``, prevents the user to write a name that is not included in the
      table related to the dbSelect. Default value in a dbSelect is ``True``
    * *validate_email*: validate an email format::
    
        root.textbox(value='^.email',validate_email=True)
        
    * *validate_empty*: add???
    * *validate_exist*: add???
    * *validate_gridnodup*: add???
    * *validate_len*: you have many options:
    
        * *validate_len=NUMBER*: set the precise lenght of the field::
        
            root.textbox(value='^.fiscal_code',validate_len='16')
            root.textbox(value='^.fiscal_code',validate_len=30)
        
        * *validate_len='NUMBER:NUMBER'*: set minimum and maximum values for field's lenght::
        
            root.textbox(value='^.name',validate_len='5:30') # from 5 to 30 digits!
            root.textbox(value='^.fiscal_code',validate_len=':16') # max number: 16
            root.textbox(value='^.surname',validate_len='2:') # at least 2 digits!
            
    * *validate_nodup*: add???
    * *validate_notnull*: if `True`, set the field as a required field::
    
        root.textbox(value='^.name', validate_notnull=True)
        root.textbox(value='^.surname', validate_notnull=True)
        
    * *validate_regex*: add???
    * *validate_remote*: add???
    
.. _validations_other_list:

other validations
=================
    
    The following validations have a small difference with a normal validation: they control
    the correct user input, and if they find it wrong, they automatically change it.
    
    * *validate_case*: you have many options:
    
        * *validate_case='c'*: (Capitalize) Set the first letter of every word uppercase
        * *validate_case='u'*: (Uppercase) Set every letter of every word uppercase
        * *validate_case='l'*: (Lowercase) Set every letter of every word lowcase
        
          Example::
          
            root.textbox(value='^.name',validate_case='c')
            root.textbox(value='^.fiscal_code',validate_case='u')
          
.. _validations_common:
    
common validations
==================
    
    **Syntax**: ``validate_`` + ``validationName_`` + ``validationAttribute``
        
    Where:
    
    * ``validate_`` is a string, common to every common validation
    * ``validationName`` is one of the Genro validations
    * ``validationAttribute`` is one of the validation attributes
    
    Here follows a complete list of the common validations:
    
    * *validate_validationName_error*: set a hint tooltip appearing on mouse click
      for user uncorrect input
      
      Example::
      
        root.textbox(value='^.email',
                     validate_email=True,
                     validate_email_error='Hint tooltip')
                     
    * *validate_validationName_onAccept*: perform a javascript action after
      a correct input
    
      Example::
      
        root.timetextbox(value='^.orario.inizio',
                         validate_onAccept="if (value){SET .orario.fine=value;}")
        root.timetextbox(value='^.orario.fine')
        
    * *validate_validationName_onReject*: perform a javascript action after
      an uncorrect input
    
      Example::
      
        root.textBox(value='^.short_string',validate_len=':10',
                     validate_onReject='alert("The string "+"\'"+value+"\'"+" is too long")')
        
.. _validations_example:

examples
========

.. _validations_form_example:

form example
------------

    ::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2)
                # In the following textbox we use the lbl attribute, because they are included in a formbuilder
                fb.textbox(value='^.name',lbl='Name', validate_case='c')
                fb.div('Capitalized field')
                fb.textbox(value='^.surname',lbl='Surname', validate_case='c')
                fb.div('Capitalized field')
                fb.textbox(value='^.job',lbl='Profession',
                           validate_case='l',
                           validate_notnull=True,validate_notnull_error='Required field!')
                fb.div('Not null field; lowercase field')
                fb.textbox(value='^.address', lbl='Address')
                fb.div('No validation is required')
                fb.textbox(value='^.fiscal_code',lbl='Fiscal code',
                           validate_len='16',validate_case='u')
                fb.div('Uppercased field; Precise length field [16]')
                fb.textBox(value='^.long',lbl='Long string',validate_len='6:',
                           validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
                fb.div('Insert 6 or more characters (wrong input notification)')
                fb.textBox(value='^.email', lbl="email", validate_email=True,
                           validate_onAccept='alert("Correct email format")',
                           validate_notnull=True)
                fb.div('required correct e-mail form (correct input notification)')
            