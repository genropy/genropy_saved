.. _genro_textboxes:

=========================
introduction to textboxes
=========================
    
    The textboxes are form widgets used to insert input data.
    
    There are different textbox types:
    
    * :ref:`genro_textbox`
    * :ref:`genro_currencytextbox`
    * :ref:`genro_datetextbox`
    * :ref:`genro_numbertextbox`
    * :ref:`genro_timetextbox`
    
    .. note:: The main additional feature to the Dojo textboxes is the compatibility with the Genro validations.
              For more information, check the :ref:`genro_validations` documentation page.
    
.. _textboxes_attributes:

Common attributes
=================

    Here we show the attributes that belong to every textbox:
    
    **commons attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information,
      check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check
      the :ref:`genro_hidden` documentation page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the
      :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath`
      documentation page
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page