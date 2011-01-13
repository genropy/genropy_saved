.. _genro_radiobutton:

===========
radiobutton
===========

	- :ref:`radiobutton_def`
	
	- :ref:`radiobutton_attributes`
	
	- :ref:`radiobutton_examples`
	
.. _radiobutton_def:

Definition and Description
==========================

	.. method:: pane.radiobutton(group=None[, **kwargs])

	Radiobuttons are used when you want to let the user select one - and just one - option from a set of choices. If more options are to be allowed at the same time you should use :ref:`genro-checkbox` instead.

.. _radiobutton_attributes:

Attributes
==========
	
	**radiobutton attributes**:
	
	* *group*: Allow to create a radiobutton group. For more information, check the example in the section below
	
	**Common attributes**:
		
	* *disabled*: if True, allow to disable this widget. Default value is ``None``. For more information, check the :ref:`genro-disabled` documentation page
	* *hidden*: if True, allow to hide this widget. Default value is ``None``. For more information, check the :ref:`genro-hidden` documentation page
	* *label*: Set the radiobutton label
	* *value*: specify the path of the widget's value. For more information, check the :ref:`genro_datapath` documentation page
	
.. _radiobutton_examples:

Example
=======

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=root.contentPane(title='Buttons',datapath='test1').formbuilder(cols=4,border_spacing='10px')
	
				fb.div("""We show you here a simple radio buttons set; (add to your radiobuttons
				          the "group" attribute).""",font_size='.9em',text_align='justify')
				fb.radiobutton(value='^.radio.jazz',group='genre1',label='Jazz')
				fb.radiobutton(value='^.radio.rock',group='genre1',label='Rock')
				fb.radiobutton(value='^.radio.blues',group='genre1',label='Blues')
	
				fb.div("""Here we show you an other radio buttons set.""",
				          font_size='.9em',text_align='justify')
				fb.div('Sex')
				fb.radiobutton(value='^.sex.male',group='genre2',label='M')
				fb.radiobutton(value='^.sex.female',group='genre2',label='F')
