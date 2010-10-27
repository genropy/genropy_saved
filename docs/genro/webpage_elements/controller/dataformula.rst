	.. _genro-dataformula:

=============
 dataFormula
=============

	- :ref:`dataformula-description`

	- :ref:`dataformula-syntax`

	- :ref:`dataformula-examples`

	.. _dataformula-description:

Description
===========

	``dataformula`` allows to insert a value into a specific address of the :ref:`genro-datastore`.

	.. _dataformula-syntax:

Syntax
======

	``object.dataformula('folderPlaceOfYourValue','formula','param','param',...)``
	
	Where:

	- first parameter: here lies the path folder in the :ref:`genro-datastore` of your value.

	- second parameter: here lies the "formula" (dataformula does not have to be necessarily a mathematical formula!)
	
	- next parameters: variables contained into the formula.

	.. _dataformula-examples:

Examples
========

	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.horizontalSlider(lbl='Base',value='^base',width='200px',minimum=1,maximum=100)
				fb.numberTextBox(value='^base',places=2)
				fb.horizontalSlider(lbl='Height',value='^height',width='200px',minimum=1,maximum=100)
				fb.numberTextBox(value='^height',places=2)
				fb.dataFormula('area','base * height', base='^base', height='^height')
				fb.numberTextBox(lbl='!!Area',value='^area',places=2,border='2px solid grey',padding='2px')
	
	Example::
	
		??? Add an example for a not mathematical usage with the dataFormula
