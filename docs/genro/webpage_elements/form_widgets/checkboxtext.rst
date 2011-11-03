.. _checkboxtext:

============
checkBoxText
============

    *Last page update*: |today|
    
    .. note:: checkBoxText features:
              
              * **Type**: :ref:`Genro form widget <genro_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`checkboxtext_def`
    * :ref:`checkboxtext_examples`:
    
        * :ref:`checkboxtext_examples_simple`
        
.. _checkboxtext_def:

definition
==========
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.checkboxtext
    
.. _checkboxtext_examples:

Examples
========

.. _checkboxtext_examples_simple:

simple example
--------------

    ::
    
        pane.checkBoxText('foo,bar,span',value='^.my_value',separator=' - ')
        pane.textbox(value='^.my_value')