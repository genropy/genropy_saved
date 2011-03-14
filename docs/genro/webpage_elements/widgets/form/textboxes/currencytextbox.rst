.. _genro_currencytextbox:

===============
currencyTextbox
===============
    
    .. note:: We recommend you to read :ref:`genro_textboxes` first.
    
    * :ref:`currencytextbox_def`
    * :ref:`currencytextBox_description`
    * :ref:`currencytextbox_attributes`
    * :ref:`currencytextbox_examples`: :ref:`currencyTextbox_examples_simple`
    
.. _currencytextbox_def:

Definition
==========

    .. method:: pane.currencyTextbox([**kwargs])

.. _currencytextBox_description:

Description
===========
    
    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.

.. _currencytextbox_attributes:

Attributes
==========

    **currencyTextbox**:
    
    * *currency*: specify used currency. Default value is ``EUR``
    * *default*: Add a default number to your widget. Default value is ``None``
    * *locale*: specify currency format type. Default value is ``it``
    
    **common attributes**:
    
        For common attributes, see :ref:`textboxes_attributes`

.. _currencytextbox_examples:

Examples
========

.. _currencytextbox_examples_simple:

simple example
--------------

    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.currencyTextBox(value='^amount',default=1123.34,
                                     currency='EUR',locale='it')	