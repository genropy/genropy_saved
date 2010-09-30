========
 Slider
========

.. currentmodule:: form

.. class:: Sliders -  Genropy sliders

	- :ref:`slider-definition`

	- :ref:`slider-where`

	- :ref:`slider-description`

	- :ref:`slider-examples`

	- :ref:`slider-attributes`
	
	- :ref:`slider-other-attributes`

	.. _slider-definition:

Definition
==========

Same definition of Dojo sliders (version 1.5). To show it, click here_.

.. _here: http://docs.dojocampus.org/dijit/form/Slider

	.. _slider-where:

Where
=====

	#NISO ???
	
	.. _slider-description:

Description
===========

	Here we introduce the sliders, form widgets inherit from Dojo. It is a scale with a handle you can drag left/right for horizontal slider (or up/down for vertical one) to select a value.


	.. _slider-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.horizontalSlider(value='^integer_number',width='200px',
									  maximum=50,discreteValues=51)

	.. _slider-attributes:

Attributes
==========

	+-------------------------+---------------------------------------------------------+-------------+
	|   Attribute             |          Description                                    |   Default   |
	+=========================+=========================================================+=============+
	| ``default='NUMBER'``    | Add a default value in your slider                      |  ``0``      |
	+-------------------------+---------------------------------------------------------+-------------+
	| ``intermediateChanges`` | (Boolean) If True, it allows to changes value of slider |  ``False``  |
	|                         | during slider move                                      |             |
	+-------------------------+---------------------------------------------------------+-------------+
	| ``maximum='NUMBER'``    | Add the maximum value of a slider                       |  ``100``    |
	+-------------------------+---------------------------------------------------------+-------------+
	| ``minimum='NUMBER'``    | Add the minimum value of a slider                       |  ``0``      |
	+-------------------------+---------------------------------------------------------+-------------+

	It is strongly advised to use "width" attribute for horizontal slider and "height" attribute for vertical slider.
	
	#NISO: ho visto che per Dojo 1.1 c'è un attributo chiamato showButtons che sembra non funzionare... (e tra l'altro c'è anche in Dojo 1.5...) la domanda è: "ci sono degli attributi che non avete riportato da Dojo, o è un errore?"

	.. slider-other-attributes:

Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the slider.          |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the slider.                                |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for slider's values.                 |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
