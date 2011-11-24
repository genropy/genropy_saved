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
    * :ref:`currencytextbox_examples`: :ref:`currencyTextbox_examples_simple`
    
.. _currencytextbox_def:

definition
==========

    .. method:: currencyTextbox([**kwargs])
    
.. _currencytextBox_description:

description
===========
    
    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but
    it is specialized for input monetary values, much like the currency type in spreadsheet programs.

.. _currencytextbox_attributes:

attributes
==========

    **currencyTextbox**:
    
    * *currency*: specify used currency
    * *locale*: specify currency format type
    
.. _currencytextbox_examples:

Examples
========

.. _currencytextbox_examples_simple:

simple example
--------------

    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.currencyTextBox(value='^amount',currency='EUR',locale='it')	