	.. _genro_timetextbox:

===========
timeTextbox
===========

    .. note:: We recommend you to read :ref:`genro_textboxes` first.
    
    * :ref:`timeTextbox_def`
    * :ref:`timeTextbox_description`
    * :ref:`timeTextbox_attributes`
    * :ref:`timeTextbox_examples`
    
.. _timeTextbox_def:

Definition
==========

    .. method:: pane.timeTextbox([**kwargs])
    
.. _timeTextbox_description:

Description
===========
    
    A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
    
    ..note:: The timeTextbox syntax is: hh:mm
    
.. _timeTextbox_attributes:

Attributes
==========

    **timeTextbox attributes**:

        There aren't particular attributes.

    **common attributes**:

        For common attributes, see :ref:`textboxes_attributes`

.. _timeTextbox_examples:

Examples
========

    Example::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.timeTextBox(value='^timeTextbox')
