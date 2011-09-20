.. _textboxes_index:

=========
Textboxes
=========
    
    *Last page update*: |today|
    
    * :ref:`textboxes`
    * :ref:`textboxes_attributes`
    * :ref:`textboxes_section_index`
    
.. _textboxes:

introduction
============

    The textboxes are form widgets used to insert input data.
    
    There are five different textbox types:
    
    * :ref:`textbox`
    * :ref:`currencytextbox`
    * :ref:`datetextbox`
    * :ref:`numbertextbox`
    * :ref:`timetextbox`
    
    .. note:: The main additional feature to the Dojo textboxes is the compatibility with the Genro validations.
              
              For more information, check the :ref:`validations` page.

.. _textboxes_attributes:

common attributes
=================

    Here we show the attributes that belong to every textbox:
    
    **commons attributes**:
    
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check
      the :ref:`hidden` page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the
      :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`datapath` page
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page
    
    We remeber also that if you want to assign a default value to any textbox, you can use
    the :ref:`data` controller
    
.. _textboxes_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    
    textbox
    currencytextbox
    datetextbox
    numbertextbox
    timetextbox