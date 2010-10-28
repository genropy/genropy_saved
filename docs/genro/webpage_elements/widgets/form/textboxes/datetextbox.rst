	.. _genro-datetextbox:

=============
 DateTextbox
=============

	- :ref:`dateTextbox-definition-description`

	- :ref:`dateTextbox-examples`

	- :ref:`dateTextbox-attributes`

	- :ref:`dateTextbox-other-attributes`

	We recommend you to read :ref:`genro-textboxes` first.

	.. _dateTextbox-definition-description:

Definition and Description
==========================

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.
    
	- syntax: GG/MM/AAAA

	.. _dateTextbox-examples:

Examples
========
	
	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.dateTextbox(value='^dateTextbox',popup=True)
		
	Let's see a demo:

	#NISO add online demo!

	.. _dateTextbox-attributes:

Attributes
==========
	
	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``left``   |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``popup``             | allow to show a calendar dialog                         |  ``True``   |
	+-----------------------+---------------------------------------------------------+-------------+
	
	.. _dateTextbox-other-attributes:

Common attributes
=================

	For common attributes, see :ref:`textboxes-attributes`
