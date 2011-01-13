	.. _genro-datetextbox:

=============
 dateTextbox
=============

	- :ref:`dateTextbox-definition-description`
	
	- :ref:`dateTextbox_attributes`
	
	- :ref:`dateTextbox-examples`

	.. note:: We recommend you to read :ref:`genro-textboxes` first.

	.. _dateTextbox-definition-description:

Definition and Description
==========================

	.. method:: pane.dateTextbox([popup=True[, **kwargs]])

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.
    
	.. note:: We remind you that the used format type of data is: dd/mm/yyyy

.. _dateTextbox_attributes:

Attributes
==========
	
	**dateTextbox attributes**:
	
	* *popup*: allow to show a calendar dialog. Default value is ``True``
	
	**common attributes**:

		For common attributes, see :ref:`textboxes_attributes`
	
	.. _dateTextbox-examples:

Examples
========
	
	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.dateTextbox(value='^dateTextbox',popup=True)
