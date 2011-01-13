	.. _genro-timetextbox:

=============
 timeTextbox
=============

	- :ref:`timeTextbox-definition-description`
	
	- :ref:`timeTextbox-attributes`
	
	- :ref:`timeTextbox_examples`

	.. note:: We recommend you to read :ref:`genro-textboxes` first.
	
	.. _timeTextbox-definition-description:

Definition and Description
==========================

	.. method:: pane.timeTextbox([**kwargs])
	
	A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
	
	..note:: The timeTextbox syntax is: hh:mm
	
	.. _timeTextbox-attributes:

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
