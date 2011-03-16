.. _genro_datetextbox:

===========
dateTextbox
===========

    .. note:: We recommend you to read :ref:`genro_textboxes` first.
    
    * :ref:`datetextbox_def`
    * :ref:`datetextbox_description`
    * :ref:`datetextbox_attributes`
    * :ref:`datetextbox_examples`: :ref:`datetextbox_examples_simple`

.. _datetextbox_def:

Definition
==========

    .. method:: pane.dateTextbox([**kwargs])

.. _datetextbox_description:

Description
===========

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.
    
    .. note:: We remind you that the used format type of data is: dd/mm/yyyy

.. _datetextbox_attributes:

Attributes
==========
    
    **dateTextbox attributes**:
    
    * *popup*: allow to show a calendar dialog. Default value is ``True``
    
    **commons attributes**:
    
        For commons attributes, see :ref:`textboxes_attributes`
        
.. _datetextbox_examples:

Examples
========

.. _datetextbox_examples_simple:

simple example
--------------

    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.dateTextbox(value='^dateTextbox',popup=True)
                