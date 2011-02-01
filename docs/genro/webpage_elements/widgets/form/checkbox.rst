	.. _genro_checkbox:

==========
 checkbox
==========

	* :ref:`checkbox_def`
	* :ref:`checkbox_attributes`
	* :ref:`checkbox_examples`
	
.. _checkbox_def:

Definition and Description
==========================

	.. method:: pane.checkbox(label=None, value=None[, **kwargs])

	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox_.
	
	.. _checkbox: http://docs.dojocampus.org/dijit/form/CheckBox

.. _checkbox_attributes:
	
Attributes
==========
	
	**checkbox attributes**:
	
		There aren't particular attributes.
	
	**common attributes**:
	
	* ``disabled``: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
	* ``hidden``: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
	* ``label``: You can't use the ``label`` attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
	* ``value``: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
	* ``visible``: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page

.. _checkbox_examples:

Examples
========

	Example::

		pane.checkbox(value='^name',label='Name')