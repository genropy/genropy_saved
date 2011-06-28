.. _genro_validations:

===========
validations
===========
    
    * :ref:`validations_intro`
    * :ref:`validations_list`
    * :ref:`validations_common`
    * :ref:`validations_example`: :ref:`validations_form_example`

.. _validations_intro:

introduction
============

    To make obligations onto user input filling out a :ref:`genro_form`,
    Genro provides an helpful developer's tool: the validations.
    
    Remember that:
    
    * The form can be saved only if all the validation requirements are satisfied.
    * You can use the validations on every single form's element of your
      :ref:`webpages_webpages` or in a :ref:`table_column` of a :ref:`genro_table`
      of your :ref:`packages_model` folder, because the validations have been
      thought to use them in :ref:`webpages_webpages` but work great also in your
      :ref:`genro_table`\s.
    * For every validation, you have a list of suffixes (explained in the
      :ref:`validations_common` section) through which you can add some features
      to the standard :ref:`validations_list` (like writing a javascript alert on
      correct/uncorrect user insertion).
    * Most of the validations have to be implemented through Python. There a few
      validations that you can use only on javascript side. If we don't specify
      anything for a validation, then it is built through Python; otherwise we specify
      that you have to implement it through Javascript.
      
.. _validations_list:

standard validations
====================

    The standard Genro validations are:
    
    * :ref:`validate_call`
    * :ref:`validate_dbselect`
    * :ref:`validate_email`
    * :ref:`validate_empty`
    * :ref:`validate_exist`
    * :ref:`validate_gridnodup`
    * :ref:`validate_len`
    * :ref:`validate_max`
    * :ref:`validate_min`
    * :ref:`validate_nodup`
    * :ref:`validate_notnull`
    * :ref:`validate_regex`
    * :ref:`validate_remote`
    
    For these validations, you can add one of these two suffixes:
    
    * *error*: Allow to warn user of his uncorrect typing (through a tooltip); user can't save the form.
      
      Example::
      
        root.textbox(value='^.email',
                     validate_email=True,
                     validate_email_error='Hint tooltip')
                     
        root.textbox(value='^.no_dot_here',
                     validate_notnull=True,validate_notnull_error='!!Required',
                     validate_regex='!\.',validate_regex_error='!!Invalid code: "." char is not allowed')
                     
    * *warning*: Allow to warn user of his uncorrect typing (through a tip); if you use the *warning*,
      user can save the form even if its typing doesn't satisfy the validations.
      
      Example::
        
        root.textBox(value='^.email2',lbl="secondary email",
                     validate_email=True,validate_email_warning='Uncorrect email format')
                     
.. _validate_call:
    
validate_call
-------------
    
    ::
    
        validate_call = """Javascript code..."""
        
    Allow to write some javascript code. The only obligation is that your code has
    to return a boolean value (`true` or `false`). If `true`, then the validation
    is satisfied; if `false`, then the validation is not satisfied and the form
    can't be saved.
    
    You can write js directly inside the validation, or you can put a name of a js
    function defined in a ``.js`` file kept into your :ref:`genro_intro_resources`.
    
    **Example:**
    
        In your webpage you will write::
        
            fb.field('fiscal_code',
                      validate_call="""return anag_methods.checkFiscalCode(value,nation);""")
                      
        where:
        
        * ``anag_methods`` is the name of a javascript variable defined in a js file called
          (for example!) ``my_functions.js``
          
        * ``checkFiscalCode`` is the name of a js function defined in the same file.
        
        In your ``my_functions.js`` you will have::
        
            var anag_methods={
                
                checkFiscalCode:function(value, nation){
                    if(value=='') return true;
                    # ...
                    # other lines of the function
                },
            
            # ... The .js file continue...
        
    Remember to use the :ref:`webpages_js_requires` to specify your js file that you use
    in your :ref:`webpages_webpages`.
    
.. _validate_dbselect:
    
validate_dbselect
-----------------
    
    ::
    
        validate_dbselect = True
    
    It is used in the :ref:`genro_dbselect` form widget.
    
    If ``True``, prevents the user to write a name that is not included in the
    table related to the dbSelect. Default value in a dbSelect is ``True``
    
.. _validate_email:
    
validate_email
--------------
    
    ::
    
        validate_email = True
    
    If ``True``, validate an email format::
    
        root.textbox(value='^.email',validate_email=True)
        
    .. note:: the ``validate_email`` use regex, so it is merely a formal control.
        
.. _validate_empty:
    
validate_empty
--------------
    
    .. deprecated:: 0.7
    
.. _validate_exist:
    
validate_exist
--------------
    
    ::
    
        validate_exist = True
        
    If ``True``, user can't save the form if the value inserted by him is not
    already in the database.
    
.. _validate_gridnodup:
    
validate_gridnodup
------------------
    
    ::
    
        validate_gridnodup = True
        
    .. note:: it can be used only inside a :ref:`genro_grid`.
    
    A validation that avoid having duplicates in a grid: it checks if the user
    insertion is already saved in the database, and validates the form if and
    only if the user input is NOT being already saved.
    
.. _validate_len:
    
validate_len
--------------
    
    ::
    
        validate_len='NUMBER:NUMBER'
        
    This validation oblige user to a precise lenght in a field user inserction::
    
        root.textbox(value='^.name',validate_len='5:30') # from 5 to 30 characters!
        root.textbox(value='^.fiscal_code',validate_len=':16') # max number: 16
        root.textbox(value='^.surname',validate_len='2:') # at least 2 characters!
        root.textbox(value='^.fiscal_code',validate_len='16')
        root.textbox(value='^.fiscal_code',validate_len=30)
        
.. _validate_max:
    
validate_max
------------
    
    ::
    
        validate_max:NUMBER
        
    Javascript validation. Max characters supported
    
.. _validate_min:
    
validate_min
------------

    ::
    
        validate_min:NUMBER
    
    Javascript validation. Min characters supported.
    
.. _validate_nodup:
    
validate_nodup
--------------
    
    ::
    
        validate_nodup = True
        
    A validation that avoid having duplicates: it checks if the user insertion
    is already saved in the database, and validates the form if and only if the
    user input is NOT being already saved.
    
.. _validate_notnull:
    
validate_notnull
----------------
    
    ::
    
        validate_notnull = True
    
    If `True`, set the field as a required field.
    
    ::
    
        tbl.column('name',validate_notnull=True)
        
    .. _validate_regex:
    
validate_regex
--------------
    
    ::
    
        validate_regex = 'WriteHereARegexExpression'
        
    Allow to create a regular expression (of the re_ Python module) that works on the field.
    
    ::
        
        validate_regex='!\.' # The field doesn't accept the "." character
        
    .. _re: http://docs.python.org/library/re.html
    
.. _validate_remote:
    
validate_remote
---------------

    ::
    
        validate_remote = 'rpcName'     # 'rpcName' is the name of your dataRpc.
        
    Allow to validate a field through a :ref:`genro_datarpc`.
    
    ::
    
        add??? (example...)
        
.. _validations_common:
    
other validations
=================

    There are also some not-standard validations (the difference is that you can't attach
    to them the *error* or the *warning* suffix)
    
    They are:
    
    * :ref:`validate_case`
    * :ref:`validate_onaccept`
    * :ref:`validate_onreject`
    
.. _validate_case:

validate_case
-------------
    
    The following validations have a small difference with a normal validation: they control
    the correct user input, and if they find it wrong, they automatically change it.
    
    You have many options (you can call them 'cult' options, just to remember their name):
    
    * *validate_case='c'* (or *validate_case='capitalize'*): Set the first letter
      of every word uppercase
    * *validate_case='u'* (or *validate_case='upper'*): Set every letter uppercase
    * *validate_case='l'* (or *validate_case='lower'*): Set every letter lowercase
    * *validate_case='t'* (or *validate_case='title'*): Set the first letter of
      the first word uppercase
      
      Example::
      
        root.textbox(value='^.name',validate_case='c')
        root.textbox(value='^.fiscal_code',validate_case='u')
        
.. _validate_onaccept:

validate_onaccept
-----------------

    Perform a javascript action after a correct user input
    
      Example::
      
        root.timetextbox(value='^.orario.inizio',
                         validate_onAccept="if (value){SET .orario.fine=value;}")
        root.timetextbox(value='^.orario.fine')
        
.. _validate_onreject:

validate_onreject
-----------------
        
    Perform a javascript action after an uncorrect user input
    
      Example::
      
        root.textBox(value='^.short_string',
                     validate_len=':10',
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
                fb = root.formbuilder(cols=2,lbl_color='teal')
                fb.div('In this example we explain you the Genro validations',
                        text_align='justify',colspan=2)
                fb.textbox(value='^.no_val',lbl='no validations here')
                fb.div("""This is a simple field: you can write anything, there is no
                          validation that check any type of correct form""",
                          font_size='0.9em',text_align='justify')
                fb.div("""The following three fields are not basic validations: they check
                          if their condition is satisfied, and if not, they correct
                          the value (so they will not give any kind of error).""",
                          text_align='justify',colspan=2)
                fb.textbox(value='^.capitalized',lbl='validate_case=\'c\'',validate_case='c')
                fb.div('Correct the field if it is not capitalized into a capitalized value',
                        font_size='0.9em',text_align='justify')
                fb.textbox(value='^.lowercased',lbl='validate_case=\'l\'',validate_case='l',
                           validate_notnull=True,validate_notnull_error='!!Required field')
                fb.div('Correct the field if it is not lowercased into a lowercased value',
                        font_size='0.9em',text_align='justify')
                fb.textbox(value='^.titled',lbl='validate_case=\'t\'',validate_case='t')
                fb.div('Correct the field if it is not titled into a titled value',
                        font_size='0.9em',text_align='justify')
                fb.div("""From now on the fields have real validations: if you don't satisfy
                          rightly their condition, the border field will become red and when
                          you return on the uncorrected field, you will get an hint on your
                          error through a tip (or a tooltip)""",
                          text_align='justify',colspan=2)
                fb.textbox(value='^.fiscal_code',lbl='validate_len=\'16\' validate_case=\'u\'',
                           validate_len='16',validate_case='u',
                           validate_len_error="""Wrong lenght: the field accept only a string
                                                 of 16 characters""")
                fb.div("""This field have a precise lenght string (16 characters) to satisfy.
                          In addition, there is an uppercase validation""",
                          font_size='0.9em',text_align='justify')
                fb.textBox(value='^.short',lbl='validate_len=\':5\'',validate_len=':5')
                fb.div('In this field you have to write a string with 5 characters max',
                        font_size='0.9em',text_align='justify')
                fb.textBox(value='^.long',lbl='validate_len=\'6:\'',validate_len='6:',
                           validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
                fb.div('In this field you have to write a string with 6 characters or more',
                        font_size='0.9em',text_align='justify')
                fb.textBox(value='^.email_error',lbl="validate_email=True",
                           validate_email=True,validate_onAccept='alert("Correct email format")')
                fb.div('This field validate an email string with regex.',
                        font_size='0.9em',text_align='justify')
                fb.textBox(value='^.email_warning',lbl="validate_email=True (warning)",
                           validate_email=True,validate_email_warning='Uncorrect email format')
                fb.div("""This field validate an email string with regex. On user error,
                          the \"validate_email_warning\" don't prevent the form to be correct.""",
                          font_size='0.9em',text_align='justify')
                fb.textbox(value='^.notnull',lbl='validate_notnull=True',
                           validate_notnull=True)