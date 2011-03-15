	.. _genro_checkbox:

========
checkbox
========

    .. note:: The Genro checkbox has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's checkbox documentation.

    * :ref:`checkbox_def`
    * :ref:`checkbox_description`
    * :ref:`checkbox_attributes`
    * :ref:`checkbox_examples`
    
.. _checkbox_def:

Definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.checkbox

.. _checkbox_description:

Description
===========

    CheckBox widgets in dijit are very intuitive and easy to use. Markup constructs for check boxes resemble the same as HTML but dojo provides more control and styling options than a conventional check box.

    Conceptually, native HTML checkboxes have 2 separate values; the first being the boolean checked state, and the second being the text value that is submitted with the containing FORM element if the checked state is true. To resolve this dichotomy, the value of a CheckBox widget is false when unchecked, but the text value when checked. Setting the value to true will check the box (but leave the submittable text string unchanged) while false will uncheck it. Setting the value to a text string will check the box and set the value to be submitted to the indicated text string.
    
.. _checkbox_attributes:
    
Attributes
==========
    
    **checkbox attributes**:
    
        There aren't particular attributes.
        
    **common attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page

.. _checkbox_examples:

Examples
========

    Example::
    
        pane.checkbox(value='^name',label='Name')