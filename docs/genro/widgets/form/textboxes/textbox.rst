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

	Textbox is a form widget used to insert data. Genro textbox is taken from Dojo ValidationTextBox (version 1.5; to show it, click here_.), so it supports all of Dojo ValidationTextBox attributes (explained below_).

	.. _here: http://docs.dojocampus.org/dijit/form/ValidationTextBox
	
	.. _where-is-it-?:

Where
=====

	#NISO ???
	
	.. _A-brief-description:

Description
===========

	Textbox is used to insert a text.
	
	.. _some-examples:

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

	.. _below:

	.. _main-attributes:

Attributes
==========
	
	+---------------------+-------------------------------------------------+--------------------------------------+
	|   Attribute         |          Description                            |   Default                            |
	+=====================+=================================================+======================================+
	| ``constraints``     | TBC #NISO ???                                   |  ``#NISO ???``                       |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``font_size``       | CSS attribute                                   |  ``1em``                             |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``invalidMessage``  | Tooltip text that appears when the content of   |  ``Il valore immesso non è valido.`` |
	|                     | the text box is invalid                         |                                      |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``promptMessage``   | Tooltip text that appears when the text box is  |  ``None`                             |
	|                     | empty and on focus                              |                                      |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``required``        | Whether the field is required or not            |  ``false``                           |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``regExp``          | Regular expression pattern to be used for       |  ``None``                            |
	|                     | validation. If this is used, do not use         |                                      |
	|                     | regExpGen                                       |                                      |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``regExpGen``       | TBC. If this is used, do not use regExp#NISO??? |  ``None``                            |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``text_align``      | CSS attribute                                   |  ``left``                            |
	+---------------------+-------------------------------------------------+--------------------------------------+
	| ``tooltipPosition`` | Define where Tooltip will appear                |  ``right``                           |
	+---------------------+-------------------------------------------------+--------------------------------------+

	.. _common-attributes:

Common attributes
=================

	For common attributes, see :doc:`textboxes`
