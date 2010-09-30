=============
 DateTextbox
=============

.. currentmodule:: form

.. class:: dateTextbox -  Genropy dateTextbox

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`common-attributes`
	
	.. _main-definition:

Definition
==========

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.
    
	- sintax: GG/MM/AAAA
	
	.. _where-is-it-?:

Where
=====

	#NISO ???

	.. _some-examples:

Examples
========
	
	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.dateTextbox(value='^dateTextbox',popup=True)
		
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
	| ``popup``             | allow to show a calendar dialog                         |  ``True``   |
	+-----------------------+---------------------------------------------------------+-------------+
	
	.. _common-attributes:

Common attributes
=================

	For common attributes, see :doc:`textboxes`
