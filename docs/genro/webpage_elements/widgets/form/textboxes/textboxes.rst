	.. _genro_textboxes:

==================================
 an Introduction to the Textboxes
==================================

	* :ref:`textboxes_introduction`
	* :ref:`textboxes_attributes`

.. _textboxes_introduction:

Definition
==========

	.. note:: The Genro textboxes have been taken from Dojo without adding any modifies. In this page and in the next one you will find some interesting features that we want to point up. For more information, check the Dojo's documentation.

	Textbox is a form widget used to insert data.

	There are different textbox types:

	* :ref:`genro_textbox`
	* :ref:`genro_currencytextbox`
	* :ref:`genro_datetextbox`
	* :ref:`genro_numbertextbox`
	* :ref:`genro_timetextbox`

.. _textboxes_attributes:

Common attributes
=================

	Here we show the attributes that belong to every textbox:

	**common attributes**:
	
	* ``disabled``: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
	* ``hidden``: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
	* ``label``: You can't use the ``label`` attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
	* ``value``: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
	* ``visible``: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page
	