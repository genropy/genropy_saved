.. _genro_disabled:

==========
 disabled
==========

	* :ref:`disabled_def`
	* :ref:`disabled_examples`: :ref:`disabled_examples_formbuilder`, :ref:`disabled_examples_standardTable`

.. _disabled_def:

Definition and description
==========================

	::
	
		disabled = False

	If ``True``, user can't act on the object (write, drag...).

	**validity:** it works on every form widget.

	.. _disabled_examples:

Examples
========

.. _disabled_examples_formbuilder:

Disabled on a formbuilder
=========================

	In the following example you can see the effect of the "disabled" attribute applied to the formbuilder: with checkbox you activate "disabled" attribute::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=root.formbuilder(datapath='test1',cols=3,fld_width='100%',width='100%',disabled='^disab')
				fb.checkbox(value='^disab',label='disable form')
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',lbl='Surname')
				fb.numberTextbox(value='^.age',lbl="Age")
				fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
				fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
				fb.textbox(value='^.job.profession',lbl='Job')
				fb.textbox(value='^.job.company_name',lbl='Company name')

.. _disabled_examples_standardTable:

Disabled on a standard table
============================

	In a :ref:`genro_standardtable` the ``disabled`` ??? continue!! (explain the lock properties...)
	