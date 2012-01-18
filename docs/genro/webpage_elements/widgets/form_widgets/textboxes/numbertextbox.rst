.. _numbertextbox:

=============
NumberTextbox
=============
    
    *Last page update*: |today|
    
    .. note:: NumberTextBox features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`numbertextbox_def`
    * :ref:`numbertextbox_examples`:
    
        * :ref:`numbertextbox_examples_simple`

.. _numbertextbox_def:

definition
==========

    .. method:: numberTextbox([**kwargs])
    
                A widget used for numerical data type
                
                * **Parameters**: **places**: Numbers of decimals. If it's reached the following
                  decimal to the last supported one, a tooltip error will warn user. Default value is ``3``
                  
.. _numbertextbox_examples:

Examples
========

.. _numbertextbox_examples_simple:

simple example
--------------

    * `numberTextbox [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/numberTextbox/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """numberTextbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_numberTextbox(self, pane):
                """numberTextbox"""
                fb = pane.formbuilder(datapath='test1', cols=2)
                fb.numberTextBox(value='^.numberTextbox')
                fb.div("""A simple number textbox. You can write any number with no more than three 
                        decimals.""", font_size='.9em', text_align='justify')
                fb.numberTextbox(value='^.numberTextbox_2', places=3)
                fb.div("With \"places=3\" you must write a number with three decimals.",
                       font_size='.9em', text_align='justify')