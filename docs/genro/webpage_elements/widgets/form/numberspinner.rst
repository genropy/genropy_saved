.. _genro_numberspinner:

=============
numberSpinner
=============

	- :ref:`numberspinner_def`
	
	- :ref:`numberspinner_attributes`
	
	- :ref:`numberspinner-examples`

.. _numberspinner_def:

Definition and Description
==========================
	
	.. note:: The Genro numberspinner has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's numberspinner_ documentation.
	
	.. _numberspinner: http://docs.dojocampus.org/dijit/form/NumberSpinner
	
	.. method:: pane.numberspinner([default=None[, min=None[, max=None]]])
	
	numberSpinner is similar to :ref:`genro_numbertextbox`, but makes integer entry easier when small adjustments are required.

	There are two features:

		* The down and up arrow buttons "spin" the number up and down.
		* Furthermore, when you hold down the buttons, the spinning accelerates to make coarser adjustments easier.

.. _numberspinner_attributes:

Attributes
==========

	**numberspinner attributes**:
	
	* *default*: add a default number to the numberSpinner. Default value is ``None``.
	* *min*: set the minimum value of the numberSpinner. Default value is ``None``.
	* *max*: set the maximum value of the numberSpinner. Default value is ``None``.
	
	**common attributes**:
		
	* *disabled*: if True, allow to disable this widget. Default value is ``None``. For more information, check the :ref:`genro-disabled` documentation page
	* *hidden*: if True, allow to hide this widget. Default value is ``None``. For more information, check the :ref:`genro-hidden` documentation page
	* *label*: You can't use the ``label`` attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
	* *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page

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