	.. _genro-textbox:

=======
textbox
=======

	- :ref:`textbox-definition-description`
	
	- :ref:`textbox_attributes`
	
	- :ref:`textbox-examples`

	.. note:: We recommend you to read :ref:`genro-textboxes` first.

	.. _textbox-definition-description:

Definition and Description
==========================

	.. method:: pane.textbox([**kwargs])

	Textbox is used to insert a text. Genro textbox is taken from Dojo ValidationTextBox (version 1.5; to show it, click here_.), so it supports all of Dojo ValidationTextBox attributes.

	.. _here: http://docs.dojocampus.org/dijit/form/ValidationTextBox

.. _textbox_attributes:

Attributes
==========
	
	**textbox attributes**:
	
	* ``constraints``: TBC ???
	* ``invalidMessage``: tooltip text that appears when the content of the textbox is invalid
	* ``promptMessage``: tooltip text that appears when the textbox is empty and on focus
	* ``required``: define if the field is a required field or not. Default value is ``False``
	* ``regExp``: regular expression pattern to be used for validation. If this is used, don't use regExpGen
	* ``regExpGen``: TBC. If this is used, do not use regExp ???. Default value is ``None``
	* ``tooltipPosition``: define where Tooltip will appear. Default value is ``right``

	**common attributes**:

		For common attributes, see :ref:`textboxes_attributes`

	.. _textbox-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.div("Some simple textboxes.",font_size='.9em',text_align='justify')
				fb = root.formbuilder(datapath='test1',cols=2)
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',lbl='Surname')
				fb.textbox(value='^.address',lbl='Address')
				fb.textbox(value='^.email',lbl='e-mail')
