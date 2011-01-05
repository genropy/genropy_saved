	.. _genro-timetextbox:

=============
 TimeTextbox
=============

	- :ref:`timeTextbox-definition-description`

	- :ref:`timeTextbox-examples`

	- :ref:`timeTextbox-attributes`

	- :ref:`timeTextbox-other-attributes`

	We recommend you to read :ref:`genro-textboxes` first.
	
	.. _timeTextbox-definition-description:

Definition and Description
==========================

    A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
    
    - syntax: HH:MM

	.. _timeTextbox-examples:

Examples
========
    
	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.timeTextBox(value='^timeTextbox')

	.. _timeTextbox-attributes:

Attributes
==========

	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``left``   |
	+-----------------------+---------------------------------------------------------+-------------+
	
	.. _timeTextbox-other-attributes:

Common attributes
=================

	For common attributes, see :ref:`textboxes-attributes`
