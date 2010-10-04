================
 Simpletextarea
================

.. currentmodule:: form

.. class:: simpleTextarea -  Genropy simpleTextarea

	- :ref:`simpleTextarea-definition`

	- :ref:`simpleTextarea-where`

	- :ref:`simpleTextarea-description`

	- :ref:`simpleTextarea-examples`

	- :ref:`simpleTextarea-attributes`

	- :ref:`simpleTextarea-other-attributes`

	.. _simpleTextarea-definition:

Definition
==========

	A simple text area.

	.. _simpleTextarea-where:

Where
=====

	#NISO ???

	.. _simpleTextarea-description:

Description
===========

	With simpletextarea you can add an area for user writing.

	.. _simpleTextarea-examples:

Examples
========

	Let's see a code example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
				                    colspan=2,color='blue',font_size='1.2em',
				                    default='A simple area to contain text.')

	Let's see a demo:

	#NISO add online demo!

	.. _simpleTextarea-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``font_size``      | CSS attribute                                   |  ``1em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``text_align``     | CSS attribute                                   |  ``left``                |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _simpleTextarea-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``default``        | Add a text to the area.                         |  ``None``                |
	|                    | For more details, see :doc:`/common/default`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the area.            |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the simpletextarea.                        |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for simpletextarea's value.          |  ``None``                |
	|                    | For more details, see :doc:`/common/datapath`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	