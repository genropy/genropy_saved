.. _timetextbox:

===========
TimeTextBox
===========
    
    *Last page update*: |today|
    
    .. note:: TimeTextBox features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
    
    * :ref:`timetextbox_def`
    * :ref:`timetextbox_description`
    * :ref:`timetextbox_examples`:
    
        * :ref:`timetextbox_examples_simple`
        
.. _timetextbox_def:

definition
==========

    .. method:: timeTextbox([**kwargs])
    
.. _timetextbox_description:

description
===========
    
    A timeTextbox it's a time input control that allow either typing time
    or choosing it from a picker widget.
    
    * The format of the timeTextbox is ``hh:mm``
    
.. _timetextbox_examples:

Examples
========

.. _timetextbox_examples_simple:

simple example
--------------

    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.timeTextBox(value='^timeTextbox')
