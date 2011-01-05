	.. _genro-simplearea:

================
 simpletextarea
================

	- :ref:`simpletextarea-definition-description`

	- :ref:`simpletextarea-examples`

	- :ref:`simpletextarea_attributes`

	- :ref:`simpletextarea-other-attributes`

	.. _simpletextarea-definition-description:

Definition and Description
==========================

	With simpletextarea you can add an area for user writing.

	.. _simpletextarea-examples:

Examples
========

	Let's see a code example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
				                    colspan=2,color='blue',font_size='1.2em',
				                    default='A simple area to contain text.')

.. _simpletextarea_attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``font_size``      | CSS attribute                                   |  ``1em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``text_align``     | CSS attribute                                   |  ``left``                |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _simpletextarea-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``default``        | Add a text to the area.                         |  ``None``                |
	|                    | For more details, see :ref:`genro-default`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the area.            |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the simpletextarea.                        |  ``False``               |
	|                    | See :ref:`genro-hidden`                         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for simpletextarea's value.          |  ``None``                |
	|                    | For more details, see :ref:`genro-datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	