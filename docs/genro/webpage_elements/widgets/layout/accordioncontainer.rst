	.. _genro-accordioncontainer:

=====================
 Accordion container
=====================

	- :ref:`accordion-definition`

	- :ref:`accordion-examples`: :ref:`accordion-simple`, :ref:`accordion_datastore`

	- :ref:`accordion-attributes`
	
	- :ref:`accordion-common-attributes`

	.. _accordion-definition:

Definition
==========
	
	Like :ref:`genro-stackcontainer` and :ref:`genro-tabcontainer`, an ``accordion container`` holds a set of panes whose titles are all visible, but only one pane's content is visible at a time. Clicking on a pane title slides the currently-displayed one away, similar to a garage door.

	.. _accordion-examples:

Examples
========

	.. _accordion-simple:

Simple example
==============

	Here we show you a simple code containing an ``accordion container``::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				ac = root.accordionContainer()
				ac.accordionPane(title='Pane one')
				ac.accordionPane(title='Pane two')
				ac.accordionPane(title='Pane three')

.. #NISO ??? Add a demo!

.. _accordion_datastore:

Datastore example
=================

	If you open the dataStore (by pressing ``ctrl+shift+D``) in a Genro webpage, you will see that it's contained into an ``accordion container`` (check the example in the :ref:`genro-datastore-examples` page).

	.. _accordion-attributes:

Attributes
==========

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``title``          | accordionContainer's children attribute.           |  ``None``                |
	|                    | Set the title of an accordionPane.                 |                          |
	+--------------------+----------------------------------------------------+--------------------------+

	.. _accordion-common-attributes:

Common attributes
=================

	For common attributes, see :ref:`genro-layout-common-attributes`