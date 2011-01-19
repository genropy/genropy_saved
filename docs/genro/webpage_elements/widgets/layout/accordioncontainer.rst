	.. _genro-accordioncontainer:

==================
accordionContainer
==================

	- :ref:`accordion-definition`
	
	- :ref:`accordion-attributes`
	
	- :ref:`accordion_examples`: :ref:`accordion_simple`
	
	.. _accordion-definition:

Definition
==========
	
	.. note:: The Genro accordionContainer has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's accordionContainer_ documentation.

	.. _accordionContainer: http://docs.dojocampus.org/dijit/layout/AccordionContainer
	
	.. method:: pane.accordionContainer([**kwargs])
	
	Like :ref:`genro-stackcontainer` and :ref:`genro_tabcontainer`, an ``accordion container`` holds a set of accordionPanes whose titles are all visible, but only one pane's content is visible at a time. Clicking on a pane title slides the currently-displayed one away, similar to a garage door.

	.. method:: pane.accordionPane([**kwargs])

	.. _accordion-attributes:

Attributes
==========

	**accordionContainer attributes**:
	
		There aren't particular attributes.
	
	**attributes of the accordionContainer's children (accordionPanes)**:
	
	* ``title``: MANDATORY - Set the accordionPane's title. Default value is ``None``

	**common attributes**:
	
		For common attributes, see :ref:`genro-layout-common-attributes`

.. _accordion_examples:

Examples
========

.. _accordion_simple:

Simple example
==============

Here we show you a simple code containing an ``accordion container``::

	class GnrCustomWebPage(object):
		def main(self,root,**kwargs):
			ac = root.accordionContainer()
			ac.accordionPane(title='Pane one')
			ac.accordionPane(title='Pane two')
			ac.accordionPane(title='Pane three')