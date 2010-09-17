=========
 Sliders
=========

.. currentmodule:: form

.. class:: Sliders -  Genropy sliders

	Here we introduce the sliders, form widgets inherit from Dojo. It is a scale with a handle you can drag left/right for horizontal slider (or up/down for vertical one) to select a value.

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
	
		Example::
			pane.horizontalSlider(value='^integer_number',width='200px',
								  maximum=50,discreteValues=51)