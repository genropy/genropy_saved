	.. _genro-checkbox:

==========
 checkbox
==========

	- :ref:`checkbox-definition-description`
	
	- :ref:`checkbox-attributes`
	
	- :ref:`checkbox-examples`
	
	.. _checkbox-definition-description:

Definition and Description
==========================

	.. method:: pane.checkbox(label=None, value=None[, **kwargs])

	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox_.
	
	.. _checkbox: http://docs.dojocampus.org/dijit/form/CheckBox

	.. _`checkbox-attributes`:
	
Attributes
==========
	
	**checkbox attributes**:
	
		There aren't particular attributes.
	
	**common attributes**:
	
	* *disabled*: if True, allow to disable this widget. Default value is ``None``. For more information, check the :ref:`genro-disabled` documentation page
	* *hidden*: if True, allow to hide this widget. Default value is ``None``. For more information, check the :ref:`genro-hidden` documentation page
	* *label*: the label of the widget.
	* *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page

	.. _checkbox-examples:

Examples
========

	Example::

		pane.checkbox(value='^name',label='Name')