.. _genro_numbertextbox:

=============
numberTextbox
=============

    .. note:: We recommend you to read :ref:`genro_textboxes` first.

    * :ref:`numbertextbox_def`
    * :ref:`numbertextbox_description`
    * :ref:`numbertextbox_attributes`
    * :ref:`numbertextbox_examples`: :ref:`numbertextbox_examples_simple`

.. _numbertextbox_def:

Definition
==========

    .. method:: pane.numberTextbox([**kwargs])
    
.. _numbertextbox_description:
    
Description
===========

    A simple number textbox.
    
.. _numbertextbox_attributes:

Attributes
==========
    
    **numberTextbox**:
    
    * *default* (or *default_value*): Add a default number to your numberTextbox. Default value is ``None``
    * *places*: Numbers of decimals. If it's reached the following decimal to the last supported one, a tooltip error will warn user. Default value is ``3``
    
    **commons attributes**:
    
        For commons attributes, see :ref:`textboxes_attributes`
        
.. _numbertextbox_examples:

Examples
========

.. _numbertextbox_examples_simple:

simple example
--------------

    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.numberTextbox(value='^numberTextbox',default=36)