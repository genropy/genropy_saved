.. _genro_datacontroller:

==============
dataController
==============

	The ``dataController`` belongs to :ref:`controllers_client` family.

	- :ref:`datacontroller_def`
	
	- :ref:`datacontroller_attr`
	
	- :ref:`datacontroller_examples`

.. _datacontroller_def:

Definition
==========
	
	.. method:: pane.dataController(script=None[, **kwargs])
	
	The ``dataController`` allow to execute a Javascript code

.. _datacontroller_attr:

Attributes
==========

	**dataController attributes**:

	* ``script``: the Javascript code that ``datacontroller`` has to execute.
	
	The following parameters allow the dataController to be executed: check for the following :ref:`datacontroller-examples` for further information.
	
	**common attributes**:
	
		For common attributes (``_init``, ``_onStart``, ``_timing``) see controllers' :ref:`controllers_attributes`

.. _datacontroller_examples:

Examples
========

	We show you two different syntaxes for the ``dataController``::
		
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = pane.borderContainer(height='200px')
				fb = bc.formbuilder(cols=2,datapath='test1')
				
				# First syntax
				fb.dataController("SET .aaa='positive number'" ,_if='shooter>=0',
				                    _else="SET .aaa='negative number'",shooter='^.x')
				fb.numberTextbox(value='^.x',lbl='x')
				fb.textbox(value='^.aaa',margin='10px',lbl='aaa')
				
				# Second syntax
				fb.dataController("""if(shooter>=0){SET .bbb='positive number';}
				                       else{SET .bbb='negative number';}""",
				                       shooter='^.y')
				fb.numberTextbox(value='^.y',lbl='y')
				fb.textbox(value='^.bbb',margin='10px',lbl='bbb')

**Footnotes**:
	
.. [#] For further details on the circumflex accent, check :ref:`datastore_syntax`.
