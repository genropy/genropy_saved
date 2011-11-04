.. _datetextbox:

===========
DateTextbox
===========
    
    *Last page update*: |today|
    
    .. note:: DateTextbox features:
    
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`datetextbox_def`
    * :ref:`datetextbox_description`
    * :ref:`datetextbox_attributes`
    * :ref:`datetextbox_examples`: :ref:`datetextbox_examples_simple`

.. _datetextbox_def:

definition
==========

    .. method:: dateTextbox([**kwargs])
    
.. _datetextbox_description:

description
===========

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing
    a date from any calendar widget.
    
    * The data format type depends on the locale parameters of your browser. For example,
      with the ``en`` locale it is set to ``mm/dd/yyyy``

.. _datetextbox_attributes:

attributes
==========
    
    **dateTextbox attributes**:
    
    * *popup*: allow to show a calendar dialog. Default value is ``True``
    
        .. image:: ../../../_images/widgets/datetextbox.png
        
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
                