	.. _checkbox:

========
CheckBox
========
    
    *Last page update*: |today|
    
    .. note:: CheckBox features:
    
              * **Type**: :ref:`Dojo form widget <dojo_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`checkbox_def`
    * :ref:`checkbox_description`
    * :ref:`checkbox_examples`:
    
        * :ref:`checkbox_examples_simple`
        
.. _checkbox_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.checkbox
        
.. _checkbox_description:

description
===========

    Conceptually, native HTML checkboxes have 2 separate values; the first being
    the boolean checked state, and the second being the text value that is submitted
    with the containing FORM element if the checked state is true. To resolve this dichotomy,
    the value of a CheckBox widget is false when unchecked, but the text value when checked.
    Setting the value to true will check the box (but leave the submittable text string
    unchanged) while false will uncheck it. Setting the value to a text string will check
    the box and set the value to be submitted to the indicated text string
    
.. _checkbox_examples:

examples
========

.. _checkbox_examples_simple:

simple example
==============

    ::
    
        pane.checkbox(value='^name',label='Name')
        