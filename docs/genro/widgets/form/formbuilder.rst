=============
 Formbuilder
=============

.. currentmodule:: form

.. class:: formbuilder -  Genropy formbuilder

	- :ref:`formbuilder-definition`

	- :ref:`formbuilder-where`

	- :ref:`formbuilder-description`

	- :ref:`formbuilder-examples`

	- :ref:`formbuilder-attributes`
	
	- :ref:`formbuilder-other-attributes`
	
	- :ref:`formbuilder-other-features`
	
		- :ref:`db-table`
		- :ref:`label-and-lbl`

	.. _formbuilder-definition:

Definition
==========
		
	Here we report formbuilder's definition::
		
		def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
	                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
	                    lblalign=None, lblvalign='middle',
	                    fldalign=None, fldvalign='middle', disabled=False,
	                    rowdatapath=None, head_rows=None, **kwargs):

	.. _formbuilder-where:

Where
=====

	You can find formbuilder in *genro/gnrpy/gnr/web/gnrwebstruct.py*

	.. _formbuilder-description:

Description
===========

With formbuilder you have an ordered place to put your HTML object; formbuilder is used in place of an HTML table.

To let you see how Genro code is simpler and more compact, we report here a comparison between an HTML table and a Genro formbuilder::
	
	HTML code:
	<table>
	    <tr>
	        <td>
	            <input type='text' value='name'/>
	        </td>
	    </tr>
	</table>
	
	Genro code:
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

	Let's see its graphical result:

	.. figure:: formbuilder.png

	.. _formbuilder-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``_class``         | For CSS style                                   |  `` ``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``border_spacing`` | CSS attribute, space between rows               |  ``6px``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``cols``           | Set columns number                              |  ``1``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :doc:`/common/attributes` |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``dbtable``        | See dbtable_ explanation                        |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fieldclass``     | CSS class appended to every formbuilder's son   |  ``gnrfield``            |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fld_width``      | Set field width                                 |  ``7em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fldalign``       | Set field horizontal align                      |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fldvalign``      | Set field vertical align                        |  ``middle``              |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``head_rows``      | #NISO ???                                       |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblalign``       | Set horizontal label alignment                  |  ``#NISO Boh!``          |
	|                    | #NISO Sembra non funzionare                     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblclass``       | Set label style                                 |  ``gnrfieldlabel``       |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblpos``         | Set label position                              |  ``L``                   |
	|                    |                                                 |                          |
	|                    | ``L``: set label on the left side of text field |                          |
	|                    |                                                 |                          |
	|                    | ``T``: set label on top of text field           |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblvalign``      | Set vertical label alignment                    |  ``middle``              |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``rowdatapath``    | #NISO ???                                       |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``tblclass``       | The standard class for formbuilder.             |  ``formbuilder``         |
	|                    |                                                 |                          |
	|                    | Actually it is the unique defined class         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
	Note: you can give CSS attributes to the field by using `fld_` followed by a CSS attribute, like::
	
		fld_color='red'
		
	In the same way (that is `lbl_` plus a CSS attribute) you can modify lbl appearences, like::
	
		lbl_width='10em'
	
Here we describe the formbuilder's field attributes:
	
	+----------------+------------------------------------------------------+--------------------------+
	|   Attribute    |       Description                                    |   default                |
	+================+======================================================+==========================+
	| ``colspan``    | Set the number of columns occupied by a single field |  ``None``                |
	+----------------+------------------------------------------------------+--------------------------+
	| ``label``      | If possible, set a label for formbuilder right field-part.                      |
	|                |                                                                                 |
	|                | For more details, check this example_.                                          |
	+----------------+---------------------------------------------------------------------------------+
	| ``lbl``        | If possible, set a label for formbuilder left field-part.                       |
	|                |                                                                                 |
	|                | For more details, check this example_.                                          |
	+----------------+------------------------------------------------------+--------------------------+
	| ``pos``        | Choose element position                              |  The first free position |
	|                |                                                      |                          |
	|                | Sintax: pos(NUMBER,NUMBER)                           |                          |
	|                |     whereas the first value represents a row,        |                          |
	|                |     the second value represents a column.            |                          |
	|                |                                                      |                          |
	|                | Other feature: "pos" accepts as a number row         |                          |
	|                | two special characters:                              |                          |
	|                |                                                      |                          |
	|                |         \+ to refer itself at the following row      |                          |
	|                |                                                      |                          |
	|                |         \* to refer itself at the current row        |                          |
	+----------------+------------------------------------------------------+--------------------------+
	| ``value``      | Set a path for formbuilder's values.                 |  ``None``                |
	|                | For more details, see :doc:`/common/datastore`       |                          |
	+----------------+------------------------------------------------------+--------------------------+

	.. _formbuilder-other-attributes:

Common attributes:
==================
	
	+--------------------+--------------------------------------------------+--------------------------+
	|   Attribute        |       Description                                |   default                |
	+====================+==================================================+==========================+
	| ``disabled``       | If True, user can't act on the object.           |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`    |                          |
	+--------------------+--------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the formbuilder/formbuilder's field         |  ``False``               |
	|                    | See :doc:`/common/hidden`                        |                          |
	+--------------------+--------------------------------------------------+--------------------------+

	.. _formbuilder-other-features:

Other features:
==============

	.. _dbtable:

	.. _db-table:
	
dbtable: an explanation
=======================
	
	The "dbtable" attribute is used to give a different path for database table in the queries of field form widget. If you don't specify it, Genro will put the value of maintable as dbtable value. Let's see two examples on "maintable", and two examples on "dbtable"::
				
		# EXAMPLE 1
		class GnrCustomWebPage(object):
			maintable='packageName.fileName'    # This is the line for maintable definition, whereas "packageName"
			                                    # is the name of the package, while "fileName" is the name of the
			                                    # model file, where lies the database.
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				
				# For specifing "maintable", you can write one of the following two lines,
				# because they have the same meaning.
				fb.field('packageName.fileName.attribute')
				fb.field('attribute')
				
		# EXAMPLE 2
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable, and so...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('packageName.fileName.attribute') # ... this is the only way to recall database.
				fb.field('attribute')                      # This line will not work!
	
	Now let's see the two examples on dbtable::
				
		# EXAMPLE 3
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('attribute',dbtable='packageName.fileName') # ... but this line works, even if you
				                                                     # haven't specified the maintable!
		# EXAMPLE 4
		class GnrCustomWebPage(object):
			maintable='shop_management.storage' # Like before, "shop_management" is the package name, while
			                                    # "storage.py" is the file name where lies database.
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('name') # This field will get "name" attribute from the "shop_management" package,
				                 # in the file named "storage".
				fb.field('name',dbtable='sell_package.employees') # This field will get "name" attribute from
				                                                  # the "sell_package" package, in the file
				                                                  # named "employees.py".
		
	For further details on "dbtable" attribute, see also :doc:`/widgets/form/field`.
	
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
	
	.. figure:: formbuilder2.png
	
	To help you in discovering of the formbuilder hidden structure we used the "border" attribute (the outcome doesn't follow the standard of beauty, but the example is instructive!).
	
	So replacing the line::
	
		fb = pane.formbuilder(datapath='test2',cols=2)
		
	with::
	
		fb = pane.formbuilder(datapath='test2',border='5px',cols=2)
	
	the effect will be:
	
	.. figure:: formbuilder3.png
	