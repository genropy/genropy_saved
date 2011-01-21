.. _genro_dataformula:

===========
dataFormula
===========

	The ``dataFormula`` belongs to :ref:`controllers_client` family.

	- :ref:`dataformula_def`

	- :ref:`dataformula_attributes`

	- :ref:`dataformula_examples`

.. _dataformula_def:

Definition
===========

	.. method:: pane.dataFormula(path, formula[, **kwargs])

	``dataFormula`` allows to insert a value into a specific address of the :ref:`genro_datastore` calculated through a formula
	
	.. note:: dataFormula does not have to be necessarily a mathematical formula!

.. _dataformula_attributes:

Attributes
==========

	* path: here lies the path folder in the :ref:`genro_datastore` of your value.
	* formula: here lies the "formula"
	* next parameters: variables contained into the formula (and ``**kwargs``)
	
.. _dataformula_examples:

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
