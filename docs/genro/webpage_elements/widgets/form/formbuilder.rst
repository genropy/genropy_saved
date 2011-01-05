	.. _genro-formbuilder:

=============
 formbuilder
=============

	- :ref:`formbuilder-description`

	- :ref:`formbuilder-examples`

	- :ref:`formbuilder_attributes`
	
	- :ref:`formbuilder-other-attributes`
	
	- :ref:`formbuilder-other-features`: :ref:`label-and-lbl`

	.. _formbuilder-description:

Description
===========

With formbuilder you have an ordered place to put your HTML object; formbuilder is used in place of an HTML table.

To let you see how Genro code is simpler and more compact, we report here a comparison between an HTML table and a Genro formbuilder::
	
	<!-- HTML code: -->
	<table>
	    <tr>
	        <td>
	            <input type='text' value='name'/>
	        </td>
	    </tr>
	</table>
	
	# Genro code:
	fb = root.formbuilder()
	fb.textbox(value='^name',lbl='Name')

In formbuilder you can put dom and widget elements; its most classic usage is to create a form made by fields and layers, and that's because formbuilder can manage automatically fields and their positioning.

	.. _formbuilder-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=root.formbuilder(datapath='test3',cols=3,fld_width='100%',width='100%')
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',colspan=2,lbl='Surname')
				fb.numberTextbox(value='^.age',lbl="Age")
				fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
				fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
				fb.textbox(value='^.job.profession',lbl='Job')
				fb.textbox(value='^.job.company_name',lbl='Company name')
				fb.textbox(value='^.job.fiscal_code',lbl='Fiscal code')

.. _formbuilder_attributes:

Attributes
==========

	For a complete list of formbuilder's attributes, check the :ref:`genro_library_gnrwebstruct` library reference page.
	
	.. note:: you can give CSS attributes to the field by using `fld_` followed by a CSS attribute, like:
	
		fld_color='red'
		
		In the same way (that is `lbl_` plus a CSS attribute) you can modify lbl appearences, like:
	
		lbl_width='10em'
	
Here we describe the formbuilder's field attributes:
	
	+----------------+------------------------------------------------------+--------------------------+
	|   Attribute    |       Description                                    |   default                |
	+================+======================================================+==========================+
	| ``colspan``    | Set the number of columns occupied by a single field |  ``None``                |
	+----------------+------------------------------------------------------+--------------------------+
	| ``label``      | If possible, set a label for formbuilder right       |  ``None``                |
	|                | field-part (more details on this example_)           |                          |
	+----------------+------------------------------------------------------+--------------------------+
	| ``lbl``        | If possible, set a label for formbuilder left        |  ``None``                |
	|                | field-part (more details on this example_)           |                          |
	+----------------+------------------------------------------------------+--------------------------+
	| ``pos``        | Choose element position                              |  The first free position |
	|                |                                                      |                          |
	|                | syntax: pos(NUMBER,NUMBER)                           |                          |
	|                |     whereas the first value represents a row,        |                          |
	|                |     the second value represents a column.            |                          |
	|                |                                                      |                          |
	|                | Other feature: "pos" accepts as a number row         |                          |
	|                | two special characters:                              |                          |
	|                |                                                      |                          |
	|                | ``+`` to refer itself at the following row           |                          |
	|                |                                                      |                          |
	|                | ``*`` to refer itself at the current row             |                          |
	+----------------+------------------------------------------------------+--------------------------+
	| ``value``      | Set a path for formbuilder's values.                 |  ``None``                |
	|                | For more details, see :ref:`genro-datapath`          |                          |
	+----------------+------------------------------------------------------+--------------------------+

	.. _formbuilder-other-attributes:

Common attributes:
==================
	
	+--------------------+--------------------------------------------------+--------------------------+
	|   Attribute        |       Description                                |   default                |
	+====================+==================================================+==========================+
	| ``disabled``       | If True, user can't act on the object.           |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`      |                          |
	+--------------------+--------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the formbuilder/formbuilder's field         |  ``False``               |
	|                    | See :ref:`genro-hidden`                          |                          |
	+--------------------+--------------------------------------------------+--------------------------+

	.. _formbuilder-other-features:

Other features
==============
	
	.. _example:
	
	.. _label-and-lbl:

label and lbl: an explanation
=============================
	
	Every formbuilder column is splitted in two parts (left one and right one): in the left one lie the values of the "lbl" attributes, while in the right one lie the values of the "label" attributes. Usually you label your form's fields with "lbl", excepted for the radiobuttons and the checkboxes on which you have to use "label" (the reason is merely visual).
	
	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = pane.formbuilder(datapath='test2',cols=2)
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',lbl='Surname')
				fb.textbox(value='^.job',lbl='Profession')
				fb.numberTextbox(value='^.age',lbl='Age')
				fb.div('Favorite sport:')
				fb.div('Favorite browser:')
				fb.checkbox(value='^.football',label='Football')
				fb.radiobutton('Internet explorer',value='^.radio1',group='genre1')
				fb.checkbox(value='^.basketball',label='Basketball')
				fb.radiobutton('Mozilla Firefox',value='^.radio2',group='genre1')
				fb.checkbox(value='^.tennis',label='Tennis')
				fb.radiobutton('Google Chrome',value='^.radio3',group='genre1')
	
	#NISO add online demo!
	
	To help you in discovering of the formbuilder hidden structure we used the "border" attribute (the outcome doesn't follow the standard of beauty, but the example is instructive!).
	
	So replacing the line::
	
		fb = pane.formbuilder(datapath='test2',cols=2)
		
	with::
	
		fb = pane.formbuilder(datapath='test2',border='5px',cols=2)
	
	the effect will be:
	
	#NISO add online demo!
