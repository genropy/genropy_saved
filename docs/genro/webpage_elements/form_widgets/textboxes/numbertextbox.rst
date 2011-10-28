.. _numbertextbox:

=============
NumberTextbox
=============
    
    *Last page update*: |today|
    
    .. note:: NumberTextBox features:
              
              * **Type**: :ref:`Dojo-improved form widget <dojo_improved_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`numbertextbox_def`
    * :ref:`numbertextbox_description`
    * :ref:`numbertextbox_attributes`
    * :ref:`numbertextbox_examples`: :ref:`numbertextbox_examples_simple`

.. _numbertextbox_def:

definition
==========

    .. method:: numberTextbox([**kwargs])
    
.. _numbertextbox_description:
    
description
===========

    A simple number textbox
    
.. _numbertextbox_attributes:

attributes
==========
    
    **numberTextbox**:
    
    * *places*: Numbers of decimals. If it's reached the following decimal to the last supported one,
      a tooltip error will warn user. Default value is ``3``
      
.. _numbertextbox_examples:

Examples
========

.. _numbertextbox_examples_simple:

simple example
--------------

    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.numberTextbox(value='^number')