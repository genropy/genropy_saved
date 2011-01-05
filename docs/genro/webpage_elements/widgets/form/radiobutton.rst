	.. _genro-radiobutton:

=============
 radiobutton
=============

	- :ref:`radiobutton-definition-description`

	- :ref:`radiobutton-examples`
	
	- :ref:`radiobutton_attributes`

	.. _radiobutton-definition-description:

Definition and Description
==========================

	Radio buttons are used when you want to let the visitor select one - and just one - option from a set of alternatives. [#]_

	.. _radiobutton-examples:

Example
=======

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=root.contentPane(title='Buttons',datapath='test1').formbuilder(cols=4,border_spacing='10px')

				fb.div("""We show you here a simple radio buttons set; (add to your radiobuttons
				          the "group" attribute).""",font_size='.9em',text_align='justify')
				fb.radiobutton(value='^.radio.jazz',group='genre1',label='Jazz')
				fb.radiobutton(value='^.radio.rock',group='genre1',label='Rock')
				fb.radiobutton(value='^.radio.blues',group='genre1',label='Blues')

				fb.div("""Here we show you an other radio buttons set.""",
				          font_size='.9em',text_align='justify')
				fb.div('Sex')
				fb.radiobutton(value='^.sex.male',group='genre2',label='M')
				fb.radiobutton(value='^.sex.female',group='genre2',label='F')

.. _radiobutton_attributes:

Attributes
==========
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``group``          | Allow to create a radio buttons group. Check    |  ``None``                |
	|                    | the following :ref:`radiobutton-examples` for   |                          |
	|                    | further details                                 |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _radiobutton-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the radiobutton.     |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the radiobutton.                           |  ``False``               |
	|                    | See :ref:`genro-hidden`                         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set radiobutton label.                          |  ``None``                |
	|                    | For more details, see :ref:`genro-label`        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for radiobutton's values.            |  ``None``                |
	|                    | For more details, see :ref:`genro-datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+

**Footnotes**:

.. [#] If more options are to be allowed at the same time you should use :ref:`genro-checkbox` instead.