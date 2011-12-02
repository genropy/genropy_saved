.. _textbox:

=======
TextBox
=======
    
    *Last page update*: |today|
    
    .. note:: TextBox features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`textbox_def`
    * :ref:`textbox_examples`:
    
        * :ref:`textbox_examples_simple`
        * :ref:`textbox_examples_validations`
        
.. _textbox_def:

definition
==========

    .. method:: textbox([**kwargs])
    
                Textbox is used to insert a text
                
                * **Parameters**:
                
                                  * **constraints**: TBC TODO
                                  * **invalidMessage**: tooltip text that appears when the content of the textbox is invalid
                                  * **promptMessage**: tooltip text that appears when the textbox is empty and on focus
                                  * **required**: define if the field is a required field or not. Default value is ``False``
                                  * **regExp**: regular expression pattern to be used for validation. If this is used, don't use regExpGen
                                  * **regExpGen**: TBC. If this is used, do not use regExp ???. Default value is ``None``
                                  * **tooltipPosition**: define where Tooltip will appear. Default value is ``right``
                  
.. _textbox_examples:

examples
========

.. _textbox_examples_simple:

simple example
--------------

    * `textbox [simple] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/textbox/1>`_
    * **Description**: 
      
      .. note:: 
                
                #. Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`formbuilder`
                   
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Textbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_textbox(self, pane):
                """Textbox"""
                fb = pane.formbuilder()
                fb.textbox(value='^.name', lbl='Name')
                fb.textbox(value='^.surname', lbl='Surname')
                fb.textbox(value='^.address', lbl='Address')
                fb.textbox(value='^.email', lbl='e-mail')
                
.. _textbox_examples_validations:

validations example
-------------------

    * `textbox [validations] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/textbox/2>`_
    * **Description**:
      
      .. note:: 
                
                #. Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`formbuilder`, :ref:`textbox`
                   
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Textbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_validation(self, pane):
                """Validation on a textbox"""
                fb = pane.formbuilder(datapath='test2', cols=2)
                fb.textbox(value='^.textBox')
                fb.div("A \"no validations\" textbox")
                fb.textbox(value='^.textBox_2', validate_len='4:')
                fb.div("""A textbox with "validate_len" validation: try to write a text with less than
                          4 characters to invalidate the field""")
                fb.textbox(value='^.textBox_2', validate_email=True)
                fb.div("""A textbox with "validate_email" validation. Try to type an email""")
        