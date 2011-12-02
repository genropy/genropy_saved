.. _currencytextbox:

===============
CurrencyTextBox
===============
    
    *Last page update*: |today|
    
    .. note:: CurrencyTextBox features:
    
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`currencytextbox_def`
    * :ref:`currencytextBox_description`
    * :ref:`currencytextbox_attributes`
    * :ref:`currencytextbox_examples`:
    
        * :ref:`currencyTextbox_examples_simple`
    
.. _currencytextbox_def:

definition
==========

    .. method:: currencyTextbox([**kwargs])
    
                The currencyTextbox inherits all the attributes and behaviors of the
                :ref:`numbertextbox` widget but it is specialized for input monetary values,
                much like the currency type in spreadsheet programs
                
                
                * **Parameters**:
                
                                  * *currency*: specify used currency
                                  * *locale*: specify currency format type
                                  
.. _currencytextbox_examples:

Examples
========

.. _currencytextbox_examples_simple:

simple example
--------------

    * `currencyTextBox [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/currencyTextbox/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """currencyTextbox"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_currencyTextbox(self, pane):
                """currencyTextbox"""
                fb = pane.formbuilder()
                fb.currencyTextBox(lbl='Amount', value='^.amount', currency='EUR', locale='it')