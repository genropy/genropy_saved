=========
 Textbox
=========

.. currentmodule:: form

.. class:: textbox -  Genropy textbox

	- :ref:`main-definition`

	- :ref:`where-is-it-?`

	- :ref:`A-brief-description`

	- :ref:`some-examples`

	- :ref:`main-attributes`
	
	- :ref:`common-attributes`

	.. _main-definition:

Definition
==========

	Textbox is a form widget used to insert data.
	
	.. _where-is-it-?:

Where
=====

	#NISO ???
	
	.. _A-brief-description:

Description
===========

	Textbox is used to insert a text.

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.div("Some simple textboxes.",font_size='.9em',text_align='justify')
				fb = root.formbuilder(datapath='test1',cols=2)
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',lbl='Surname')
				fb.textbox(value='^.address',lbl='Address')
				fb.textbox(value='^.email',lbl='e-mail')

	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

Attributes
==========
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``font_size``      | CSS attribute                                   |  ``1em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``text_align``     | CSS attribute                                   |  ``left``                |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _common-attributes:

Common attributes
=================

	For common attributes, see :doc:`textboxes`
