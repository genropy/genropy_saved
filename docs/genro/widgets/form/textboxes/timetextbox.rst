=============
 TimeTextbox
=============

.. currentmodule:: form

.. class:: timeTextbox -  Genropy timeTextbox

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`common-attributes`
	
	.. _main-definition:

Definition
==========

    A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
    
    - sintax: HH:MM

Where
=====

	#NISO ???

	.. _some-examples:

Examples
========
    
	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.timeTextBox(value='^timeTextbox')

	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

Attributes
==========

	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``left``   |
	+-----------------------+---------------------------------------------------------+-------------+
