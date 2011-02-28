.. _genro_datetextbox:

=============
 dateTextbox
=============

    .. note:: We recommend you to read :ref:`genro_textboxes` first.
    
    * :ref:`dateTextbox_def`
    * :ref:`dateTextbox_description`
    * :ref:`dateTextbox_attributes`
    * :ref:`dateTextbox_examples`

.. _dateTextbox_def:

Definition
==========

    .. method:: pane.dateTextbox([**kwargs])

.. _dateTextbox_description:

Description
===========

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.
    
    .. note:: We remind you that the used format type of data is: dd/mm/yyyy

.. _dateTextbox_attributes:

Attributes
==========
    
    **dateTextbox attributes**:
    
    * ``popup``: allow to show a calendar dialog. Default value is ``True``
    
    **common attributes**:
    
        For common attributes, see :ref:`textboxes_attributes`
        
.. _dateTextbox_examples:

Examples
========
    
    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.dateTextbox(value='^dateTextbox',popup=True)
                