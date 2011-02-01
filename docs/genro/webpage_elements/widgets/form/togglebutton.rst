.. _genro_togglebutton:

==============
 togglebutton
==============

	* :ref:`togglebutton_def`
	* :ref:`togglebutton_attributes`
	* :ref:`togglebutton_examples`

.. _togglebutton_def:

Definition and Description
==========================

	.. method:: pane.togglebutton(label=None[, **kwargs])
	
	A toggle button is a button that represents a setting with a ``True`` or ``False`` state. Togglebuttons look similar to command buttons and display a graphic or text (or both) to identify themselves.

.. _togglebutton_attributes:

Attributes
==========
	
	**togglebutton attributes**:
	
	* ``iconClass``: CSS attribute to insert a button image. Default value is ``None``. If you want to use the togglebutton as a boolean widget, we recommend you to use ``iconClass="dijitRadioIcon"``, like in the following line code [#]_::
		
		fb.togglebutton(value='^.toggle1', iconClass="dijitRadioIcon", label='a togglebutton')
			
	**common attributes**:
	
	* ``disabled``: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
	* ``hidden``: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
	* ``label``: the togglebutton label
	* ``value``: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
	* ``visible``: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page

.. _togglebutton_examples:

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

**Footnotes**:

.. [#] This allow the user to check the actual state of the button (``True`` or ``False``).