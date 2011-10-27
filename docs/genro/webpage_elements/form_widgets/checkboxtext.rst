.. _checkboxtext:

============
checkBoxText
============

    *Last page update*: |today|
    
    .. note:: **Type**: :ref:`Genro form widget <genro_form_widgets>`
    
    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.checkboxtext
        
    **commons attributes**:
    
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`hidden` page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget,
      check the :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`datapath` page
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page
    
    **example**::
    
        pane.checkBoxText('foo,bar,span',value='^.my_value',separator=' - ')
        pane.textbox(value='^.my_value')