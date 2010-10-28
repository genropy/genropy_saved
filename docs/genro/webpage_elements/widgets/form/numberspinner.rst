	.. _genro-numberspinner

===============
 numberSpinner
===============

	- :ref:`numberspinner-definition-description`
	
	- :ref:`numberspinner-examples`

	- :ref:`numberspinner-attributes`

	- :ref:`numberspinner-other-attributes`

	.. _numberspinner-definition-description:

Definition and Description
==========================
	
	numberSpinner is similar to :ref:`genro-numbertextbox`, but makes integer entry easier when small adjustments are required.

	There are two features:

		- The down and up arrow buttons "spin" the number up and down.
		- Furthermore, when you hold down the buttons, the spinning accelerates to make coarser adjustments easier.

	.. _numberspinner-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = root	.formbuilder(datapath='test1',cols=2)
				fb.numberSpinner(value='^.number',default=100,min=0,lbl='number')
				fb.div("""Try to hold down a button: the spinning accelerates to make coarser
				          adjustments easier""", font_size='.9em',text_align='justify',margin='5px')

	Let's see a demo:

	#NISO add online demo!

	.. _numberspinner-attributes:

Attributes
==========
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``font_size``      | CSS attribute                                   |  ``1em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``text_align``     | CSS attribute                                   |  ``left``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``default``        | Add a default number to the numberSpinner       |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``min=NUMBER``     | set min value of numberSpinner                  |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``max=NUMBER``     | set max value of numberSpinner                  |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _numberspinner-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the numberspinner.   |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the numberspinner.                         |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set numberspinner label.                        |  ``None``                |
	|                    | For more details, see :ref:`genro-label`        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for numberspinner's values.          |  ``None``                |
	|                    | For more details, see :ref:`genro-datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+

