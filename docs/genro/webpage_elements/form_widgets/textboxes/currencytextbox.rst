.. _currencytextbox:

===============
currencyTextbox
===============
    
    *Last page update*: |today|
    
    **Type**: :ref:`Dojo-improved form widget <dojo_improved_form_widgets>`
    
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
    
    * *currency*: specify used currency. Default value is ``EUR``
    * *locale*: specify currency format type. Default value is ``it``
    
    **commons attributes**:
    
        For commons attributes, see :ref:`textboxes_attributes`

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