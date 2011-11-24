.. _validations:

===========
validations
===========
    
    *Last page update*: |today|
    
    * :ref:`validations_intro`
    * :ref:`validations_list`:
    
        * :ref:`validate_dbselect`
        * :ref:`validate_email`
        * :ref:`validate_empty`
        * :ref:`validate_exist`
        * :ref:`validate_gridnodup`
        * :ref:`validate_len`
        * :ref:`validate_nodup`
        * :ref:`validate_notnull`
        * :ref:`validate_regex`
        
    * :ref:`validations_js_list`:
    
        * :ref:`validate_call`
        * :ref:`validate_case`
        * :ref:`validate_max`
        * :ref:`validate_min`
        * :ref:`validate_onaccept`
        * :ref:`validate_onreject`
        * :ref:`validate_remote`
        
    * :ref:`validations_suffixes`:
    
        * :ref:`validations_suffix_error`
        * :ref:`validations_suffix_warning`
        
    * :ref:`validations_example`: :ref:`validations_form_example`
    
.. _validations_intro:

introduction
============

    To make obligations onto user input filling out a :ref:`form`, Genro provides an
    helpful developer's tool: the validations.
    
    * You can use the validations on every single form's element of your :ref:`webpage`
    * User can save the record created through the :ref:`form` only if all the requirements
      of every validation of the form have been satisfied
    
    There are two types of validations:
    
        #. :ref:`validations_list` - handled on server
        #. :ref:`validations_js_list` - handled on client
        
    Some useful notes about them:
    
    * The :ref:`validations_list` can be used both on :ref:`webpages <webpage>` and on the
      :ref:`columns` of a :ref:`database table <table>`:  if you set a validation on a webpage
      then the validation will work only during the webpage insertion of a record
    * the :ref:`validations_js_list` can be used only in the :ref:`webpages <webpage>`, not
      in the :ref:`database tables <table>`
    * There are some suffixes (explained in the :ref:`validations_suffixes` section) that allow
      to add some additional features (like writing a javascript alert on correct/uncorrect user
      insertion): they work on all the :ref:`validations_list` and work on most of the
      :ref:`validations_js_list`
      
.. _validations_list:

python validations
==================

    The python validations are:
    
    * :ref:`validate_dbselect`: a tool of the :ref:`dbselect`
    * :ref:`validate_email`: allow to validate an email format
    * :ref:`validate_empty`: deprecated validation
    * :ref:`validate_exist`: allow to check the existence of a field in the database
    * :ref:`validate_gridnodup`: allow to avoid having duplicates in a grid
    * :ref:`validate_len`: oblige user to use a precise lenght in a field insertion
    * :ref:`validate_nodup`: allow to avoid having duplicates in the database
    * :ref:`validate_notnull`: allow to set a field as a required field
    * :ref:`validate_regex`: allow to impose a regular expression (of the re_ Python module) validation on the field
    
.. _validate_dbselect:
    
validate_dbselect
-----------------
    
    ::
    
        validate_dbselect = True
    
    It is used in the :ref:`dbselect` form widget.
    
    If ``True``, prevents the user to write a name that is not included in the
    table related to the dbSelect. Default value in a dbSelect is ``True``
    
.. _validate_email:
    
validate_email
--------------
    
    ::
    
        validate_email = True
    
    If ``True``, validate an email format::
    
        root.textbox(value='^.email',validate_email=True)
        
    .. note:: the ``validate_email`` use regex, so it is merely a formal control
        
.. _validate_empty:
    
validate_empty
--------------
    
    .. warning:: deprecated since version 0.7
    
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
        
    .. note:: it can be used only inside a :ref:`grid`
    
    A validation that avoid having duplicates in a grid: it checks if the user
    insertion is already saved in the database, and validates the form if and
    only if the user input is NOT being already saved.
    
.. _validate_len:
    
validate_len
--------------
    
    ::
    
        validate_len='NUMBER:NUMBER'
        
    This validation oblige user to a precise lenght in a field user insertion::
    
        root.textbox(value='^.name',validate_len='5:30') # from 5 to 30 characters!
        root.textbox(value='^.fiscal_code',validate_len=':16') # max number: 16
        root.textbox(value='^.surname',validate_len='2:') # at least 2 characters!
        root.textbox(value='^.fiscal_code',validate_len='16')
        root.textbox(value='^.fiscal_code',validate_len=30)
        
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
    
    If `True`, set a field as a required field.
    
    ::
    
        tbl.column('name',validate_notnull=True)
        
    .. _validate_regex:
    
validate_regex
--------------
    
    ::
    
        validate_regex = 'WriteHereARegexExpression'
        
    Allow to impose a regular expression (of the re_ Python module) validation on the field.
    
    ::
        
        validate_regex='!\.' # The field doesn't accept the "." character
        
    .. _re: http://docs.python.org/library/re.html
    
.. _validations_js_list:

javascript validations
======================

    The javascript validations work on client side, so if you use them in a :ref:`project` remember
    that they can be used only in the :ref:`webpages <webpage>`, not in the :ref:`database tables <table>`.
    
    Some of them support the :ref:`validations_suffixes`: for every validation you find
    if the suffixes are supported or not.
    
    They are:
    
    * :ref:`validate_call`: allow to write javascript code or to import javascript functions to perform
      a validation
    * :ref:`validate_case`: check the case and modify it if it is not corresponding to the request
    * :ref:`validate_max`: set the max characters supported
    * :ref:`validate_min`: set the min characters supported
    * :ref:`validate_onaccept`: perform a javascript action after a correct user input
    * :ref:`validate_onreject`: perform a javascript action after an uncorrect user input
    * :ref:`validate_remote`: javascript validation. Allow to validate a field through a :ref:`datarpc`
    
.. _validate_call:
    
validate_call
-------------
    
    .. note:: :ref:`validations_suffixes` supported
    
    ::
    
        validate_call = """javascript code..."""
        
    Allow to write some javascript code. The only obligation is that your code has
    to return a boolean value (`true` or `false`). If `true`, then the validation
    is satisfied; if `false`, then the validation is not satisfied and the form
    can't be saved.
    
    You can write js directly inside the validation, or you can put a name of a js
    function defined in a ``.js`` file kept into your :ref:`intro_resources`.
    
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
        
    Remember to use the :ref:`webpages_js_requires` to specify your js file
    that you use in your :ref:`webpage`
    
.. _validate_case:

validate_case
-------------

    .. note:: :ref:`validations_suffixes` not supported
    
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
        
.. _validate_max:
    
validate_max
------------

    .. note:: :ref:`validations_suffixes` supported
    
    ::
    
        validate_max:NUMBER
        
    javascript validation. Max characters supported
    
.. _validate_min:
    
validate_min
------------

    .. note:: :ref:`validations_suffixes` supported
    
    ::
    
        validate_min:NUMBER
    
    javascript validation. Min characters supported.
    
.. _validate_remote:
    
validate_remote
---------------

    .. note:: :ref:`validations_suffixes` supported
    
    Allow to validate a field through a :ref:`datarpc`.
    
    Inside the dataRpc you can write some code that have to return:
    
    * ``True``, when the conditions required from the validation have been satisified
    * ``False``, when the conditions required haven't been satisfied
    
    You can pass the dataRpc as a string::
        
        validate_remote = 'RpcName'     # 'RpcName' is the name of the dataRpc
        
    or you can pass it as a callable::
    
        validate_remote = self.RpcName
        
    where ``RpcName`` is the name of the dataRpc defined through the
    :meth:`~gnr.core.gnrdecorator.public_method` decorator. For more information,
    check the :ref:`datarpc_callable` section
    
    **Example**:
    
        Let's see an example in a :ref:`webpage`:
        
        #. To pass the dataRpc method as a callable you have to use the
           :meth:`~gnr.core.gnrdecorator.public_method` decorator; so,
           you have to import::
           
            from gnr.core.gnrdecorator import public_method
            
        #. We pass now the dataRpc as a callable into a :ref:`field` including
           the :ref:`validate_remote`::
           
            root.field('id_rate',
                        validate_remote=self.check_rate, validate_remote_error='Error!')
                        
        #. We define now the dataRpc as :meth:`~gnr.core.gnrdecorator.public_method`
        
            ::
            
                @public_method                    
                def check_rate(self,**kwargs):
                    return something # Here goes the code for the validate_remote, that must
                                     #    return "True" if the conditions have been satisfied,
                                     #    "False" if the conditions haven't been satisfied
                                     
.. _validate_onaccept:

validate_onAccept
-----------------

    .. note:: :ref:`validations_suffixes` not supported
    
    Perform a javascript action after a correct user input
    
      Example::
      
        root.timetextbox(value='^.orario.inizio',
                         validate_onAccept="if (value){SET .orario.fine=value;}")
        root.timetextbox(value='^.orario.fine')
        
        
        TODO spiegare il value!! (o rimandare a pagina javascript se è una cosa comune...)
        
        fb.field('data_scadenza', validate_onAccept="""if(value < min){return false;}""",
                                  validate_min='^.data_emissione')
        
.. _validate_onreject:

validate_onReject
-----------------

    .. note:: :ref:`validations_suffixes` not supported
    
    Perform a javascript action after an uncorrect user input
    
      Example::
      
        root.textBox(value='^.short_string',
                     validate_len=':10',
                     validate_onReject='alert("The string "+"\'"+value+"\'"+" is too long")')
                     
.. _validations_suffixes:

common suffixes 
===============

    For the :ref:`validations_list` and most of the :ref:`validations_js_list`, you can add one
    of these following suffixes:
    
    #. :ref:`validations_suffix_error`
    #. :ref:`validations_suffix_warning`
    
.. _validations_suffix_error:

error
-----
    
    Allow to warn user of his uncorrect typing (through a tooltip); user can't save the :ref:`form`
    
       **Example**::
       
         root.textbox(value='^.email',
                      validate_email=True,
                      validate_email_error='Hint tooltip')
                      
         root.textbox(value='^.no_dot_here',
                      validate_notnull=True,validate_notnull_error='!!Required',
                      validate_regex='!\.',validate_regex_error='!!Invalid code: "." char is not allowed')
                      
.. _validations_suffix_warning:

warning
-------
                      
    Allow to warn user of his uncorrect typing (through a tip); if you use the *warning*,
    user can save the :ref:`form` even if its typing doesn't satisfy the validations
       
       **Example**::
         
         root.textBox(value='^.email2',lbl="secondary email",
                      validate_email=True,validate_email_warning='Uncorrect email format')
                     
.. _validations_example:

examples
========

.. _validations_form_example:

form example
------------

    An example with validations. They are kept ordered through the :ref:`formbuilder` attribute::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fs='1.2em'
                fs_small='1em'
                ta='justify'
                fb = root.formbuilder(cols=2,lbl_color='teal')
                fb.textbox(value='^.no_val',lbl='no validations here')
                fb.div("""This is a simple field: you can write anything, there is no
                          validation that check any type of correct form""",
                          font_size=fs_small,text_align=ta)
                fb.div("""The following four validations check if their condition is satisfied,
                          and if not, they correct the value (so they will not give any kind of error).""",
                          font_size=fs,text_align=ta,colspan=2)
                fb.textbox(value='^.c',lbl='validate_case=\'c\'',validate_case='c')
                fb.div('Correct the field if it is not capitalized into a capitalized value',
                        font_size=fs_small,text_align=ta)
                fb.textbox(value='^.u',lbl='validate_case=\'u\'',validate_case='u')
                fb.div('Correct the field if it is not uppercased into a uppercased value',
                        font_size=fs_small,text_align=ta)
                fb.textbox(value='^.l',lbl='validate_case=\'l\'',validate_case='l',
                           validate_notnull=True,validate_notnull_error='!!Required field')
                fb.div('Correct the field if it is not lowercased into a lowercased value',
                        font_size=fs_small,text_align=ta)
                fb.textbox(value='^.t',lbl='validate_case=\'t\'',validate_case='t')
                fb.div('Correct the field if it is not titled into a titled value',
                        font_size=fs_small,text_align=ta)
                fb.div("""From now on the fields have real validations: if you don't satisfy
                          rightly their condition, the border field will become red and when
                          you return on the uncorrected field, you will get an hint on your
                          error through a tip (or a tooltip)""",
                          font_size=fs,text_align=ta,colspan=2)
                fb.textbox(value='^.fiscal_code',lbl='validate_len=\'16\'',
                           validate_len='16',
                           validate_len_error="""Wrong lenght: the field accept only a string
                                                 of 16 characters""")
                fb.div("""This field have a precise lenght string (16 characters) to satisfy.
                          In addition, there is an uppercase validation""",
                          font_size=fs_small,text_align=ta)
                fb.textBox(value='^.short',lbl='validate_len=\':5\'',validate_len=':5')
                fb.div('In this field you have to write a string with 5 characters max',
                        font_size=fs_small,text_align='justify')
                fb.textBox(value='^.long',lbl='validate_len=\'6:\'',validate_len='6:',
                           validate_onReject='alert("The string "+"\'"+value+"\'"+" is too short")')
                fb.div('In this field you have to write a string with 6 characters or more',
                        font_size=fs_small,text_align=ta)
                fb.textBox(value='^.email_error',lbl="validate_email=True",
                           validate_email=True,validate_onAccept='alert("Correct email format")')
                fb.div('This field validate an email string with regex.',
                        font_size=fs_small,text_align=ta)
                fb.textBox(value='^.email_warning',lbl="validate_email=True (warning)",
                           validate_email=True,validate_email_warning='Uncorrect email format')
                fb.div("""This field validate an email string with regex. On user error,
                          the \"validate_email_warning\" don't prevent the form to be correct.""",
                          font_size=fs_small,text_align=ta)
                fb.textbox(value='^.notnull',lbl='validate_notnull=True',
                           validate_notnull=True)
                fb.div('A mandatory field', font_size=fs_small,text_align=ta)