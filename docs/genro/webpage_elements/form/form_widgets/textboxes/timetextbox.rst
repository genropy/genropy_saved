	.. _genro_timetextbox:

===========
timeTextbox
===========

    .. note:: We recommend you to read :ref:`genro_textboxes` first.
    
    * :ref:`timetextbox_def`
    * :ref:`timetextbox_description`
    * :ref:`timetextbox_attributes`
    * :ref:`timetextbox_examples`: :ref:`timetextbox_examples_simple`
    
.. _timetextbox_def:

Definition
==========

    .. method:: pane.timeTextbox([**kwargs])
    
.. _timetextbox_description:

Description
===========
    
    A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
    
    ..note:: The timeTextbox syntax is: hh:mm
    
.. _timetextbox_attributes:

Attributes
==========

    **timeTextbox attributes**:

        There aren't particular attributes.

    **commons attributes**:

        For commons attributes, see :ref:`textboxes_attributes`

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
