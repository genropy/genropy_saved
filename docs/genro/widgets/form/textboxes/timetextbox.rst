	.. _textboxes-timetextbox:

=============
 TimeTextbox
=============

.. currentmodule:: form

.. class:: timeTextbox -  Genropy timeTextbox

	- :ref:`timeTextbox-definition`
	
	- :ref:`timeTextbox-where`
	
	- :ref:`timeTextbox-examples`
	
	- :ref:`timeTextbox-attributes`
	
	- :ref:`timeTextbox-other-attributes`
	
	.. _timeTextbox-definition:

Definition
==========

    A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
    
    - sintax: HH:MM

	.. _timeTextbox-where:

Where
=====

	#NISO ???

	.. _timeTextbox-examples:

Examples
========
    
	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.timeTextBox(value='^timeTextbox')

	Let's see a demo:

	#NISO add online demo!

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
