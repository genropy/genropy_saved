	.. _genro-togglebutton:

==============
 togglebutton
==============

	- :ref:`togglebutton-definition-description`

	- :ref:`togglebutton-examples`

	- :ref:`togglebutton-attributes`

	- :ref:`togglebutton-other-attributes`

	.. _togglebutton-definition-description:

Definition and Description
==========================

	A toggle button is a button that represents a setting with a ``True`` or ``False`` state. Toggle buttons look similar to command buttons and display a graphic or text (or both) to identify themselves.

	.. _togglebutton-examples:

Examples
========

	Let's see a code example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.div('We show you here a simple togglebuttons set:',
				          font_size='.9em',text_align='justify')
				fb=root.formbuilder(border_spacing='10px',datapath='test1')
				fb.togglebutton(value='^.toggle1',iconClass="dijitRadioIcon",label='label')
				fb.togglebutton(value='^.toggle2',iconClass="dijitRadioIcon",label='another label')

	.. _togglebutton-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``iconClass``      | CSS attribute, use it to insert a button image  |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _togglebutton-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the togglebutton.    |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the togglebutton.                          |  ``False``               |
	|                    | See :ref:`genro-hidden`                         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set togglebutton label.                         |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for togglebutton's values.           |  ``None``                |
	|                    | For more details, see :ref:`genro_datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	