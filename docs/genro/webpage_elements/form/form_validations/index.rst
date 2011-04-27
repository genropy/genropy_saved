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
    
    Remember that:
    
    * You can use the validations on every single form's element.
    * The form can be saved only if all the validation requirements are satisfied.
    * For every validation, you have a list of suffixes (:ref:`validations_common`)
      through which you can add some features to the standard :ref:`validations_list`
      (like writing a javascript alert on correct/uncorrect user insertion).
    * Most of the validations have to be implemented through Python. So, if we don't
      specify anything, a validation is built through Python. Otherwise, we specify
      that you have to implement it through Javascript.
      
.. _validations_list:

Genro validations
=================

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
    * *validate_len='NUMBER:NUMBER'*: set the lenght of the field::
    
        root.textbox(value='^.name',validate_len='5:30') # from 5 to 30 characters!
        root.textbox(value='^.fiscal_code',validate_len=':16') # max number: 16
        root.textbox(value='^.surname',validate_len='2:') # at least 2 characters!
        root.textbox(value='^.fiscal_code',validate_len='16')
        root.textbox(value='^.fiscal_code',validate_len=30)
        
    * *validate_max:NUMBER*: Javascript validation. Max characters supported.
    * *validate_min:NUMBER*: Javascript validation. Min characters supported.
    * *validate_nodup*: add???
    * *validate_notnull*: if `True`, set the field as a required field::
    
        root.textbox(value='^.name', validate_notnull=True)
        root.textbox(value='^.surname', validate_notnull=True)
        
    * *validate_regex*: allow to create a regular expression (of the re_ Python module) that works on the field::
        
        validate_regex='!\.' # The field doesn't accept the "." character
        
    .. _re: http://docs.python.org/library/re.html
    
    * *validate_remote*: add???
    
.. _validations_other_list:

other validations
=================
    
    The following validations have a small difference with a normal validation: they control
    the correct user input, and if they find it wrong, they automatically change it.
    
    * *validate_case*: you have many options:
    
        * *validate_case='c'* (or *validate_case='capitalize'*): Set the first letter
          of every word uppercase
        * *validate_case='t'* (or *validate_case='title'*): Set the first letter of
          the first word uppercase
        * *validate_case='u'* (or *validate_case='upper'*): Set every letter uppercase
        * *validate_case='l'* (or *validate_case='lower'*): Set every letter lowercase
        
          Example::
          
            root.textbox(value='^.name',validate_case='c')
            root.textbox(value='^.fiscal_code',validate_case='u')
          
.. _validations_common:
    
suffixes to validations
=======================
    
    **Syntax**: ``validationName_`` + ``validationAttribute``
    
    Where:
    
    * ``validationName`` is one of the :ref:`validations_list` showed before
      (e.g: ``validate_email``, ``validate_regex``)
    * ``validationAttribute`` is one of the following validations:
    
        * *error*: Allow to warn user of his uncorrect typing (through a tooltip); user can't save the form::
          
          Example::
          
            root.textbox(value='^.email',
                         validate_email=True,
                         validate_email_error='Hint tooltip')
                         
            root.textbox(value='^.no_dot_here',
                         validate_notnull=True,validate_notnull_error='!!Required',
                         validate_regex='!\.',validate_regex_error='!!Invalid code: "." char is not allowed')
                         
        * *onAccept*: perform a javascript action after a correct input
        
          Example::
          
            root.timetextbox(value='^.orario.inizio',
                             validate_onAccept="if (value){SET .orario.fine=value;}")
            root.timetextbox(value='^.orario.fine')
            
        * *onReject*: perform a javascript action after an uncorrect input
        
          Example::
          
            root.textBox(value='^.short_string',validate_len=':10',
                         validate_onReject='alert("The string "+"\'"+value+"\'"+" is too long")')
        
        * *warning*: Allow to warn user of his uncorrect typing (through a tip); if you use the *warning*,
          user can save the form even if he was wrong to write.
          
          Example::
            
            root.textBox(value='^.email2',lbl="secondary email",
                         validate_email=True,validate_email_warning='Uncorrect email format')
                         
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
                