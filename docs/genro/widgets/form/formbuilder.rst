=============
 formbuilder
=============

.. currentmodule:: form

.. class:: formbuilder -  Genropy formbuilder

**Index:**

	- Definition_
	
	- Where_
	
	- Description_
	
	- Examples_
	
	- Attributes_
	
	- Other features:
	
		- dbtable_: an explanation of the attribute
		- label and lbl: an explanation_.

.. _Definition:

**Definition**::
	
		def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
	                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
	                    lblalign=None, lblvalign='middle',
	                    fldalign=None, fldvalign='middle', disabled=False,
	                    rowdatapath=None, head_rows=None, **kwargs):

.. _Where:

**Where:**

	You can find formbuilder in *genro/gnrpy/gnr/web/gnrwebstruct.py*
	
.. _Description:

**Description:**

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

.. _Examples:

**Examples**:

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test3',cols=3,fld_width='100%',width='100%')
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

.. _Attributes:

**Attributes**:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``_class``         | For CSS style                                   |  `` ``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``border_spacing`` | CSS attribute, space between rows               |  ``6px``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``cols``           | Set columns number                              |  ``1``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``datapath``       | See :doc:`/common/attributes`                   |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``dbtable``        | See dbtable_ explanation                        |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | See :doc:`/common/attributes`                   |  ``False``               |
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
	| ``hidden``         | See :doc:`/common/attributes`                   |  ``False``               |
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
	
Here we describe the formbuilder's field attributes:
	
	+----------------+------------------------------------------------------+--------------------------+
	|   Attribute    |       Description                                    |   default                |
	+================+======================================================+==========================+
	| ``colspan``    | Set the number of columns occupied by a single field |  ``None``                |
	+----------------+------------------------------------------------------+--------------------------+
	| ``hidden``     | See :doc:`/common/attributes`                        |  ``False``               |
	+----------------+------------------------------------------------------+--------------------------+
	| ``label``      | Set field right label - for more details, check this example_.                  |
	+----------------+---------------------------------------------------------------------------------+
	| ``lbl``        | Set field left label - for more details, check this example_.                   |
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
	| ``value``      | See :doc:`/common/attributes`                        |  ``None``                |
	+----------------+------------------------------------------------------+--------------------------+

**Other features:**
		
.. _dbtable:
	
**dbtable: an explanation of the attribute**
	
	The "dbtable" attribute is used to give a different path for database table in the queries of field form widget. If you don't specify it, Genro will put the value of maintable as dbtable value. Let's see two examples on "maintable", and two examples on "dbtable"::
	
		EXAMPLE 1:
		
		class GnrCustomWebPage(object):
		    maintable='packageName.fileName'	# This is the line for maintable definition, whereas "packageName"
		                                        # is the name of the package, while "fileName" is the name of the model
		                                        # file, where lies the database.
		
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				
				# For specifing "maintable", you can write one of the following two lines,
				# because they have the same meaning.
				fb.field('packageName.fileName.attribute')
				fb.field('attribute')
				
		EXAMPLE 2:
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable, and so...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('packageName.fileName.attribute') # ... this is the only way to recall database.
				fb.field('attribute')                      # This line will not work!
	
	Now let's see the two examples on dbtable::
				
		EXAMPLE 3:
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('attribute',dbtable='packageName.fileName') # ... but this line works, even if you
				                                                     # haven't specified the maintable!
		EXAMPLE 4:
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
		
	For further details on "dbtable" attribute, see also :doc:`/widgets/form/field`
	
.. _example:

.. _explanation:

**label and lbl: an explanation**:
	
	Every formbuilder column is splitted in two parts (left one and right one): the right part is the one where user can compile fields, while the left part is where "lbl" attribute appear. You can also see the effect of "border_spacing" css attribute, that is the space between fields. Last thing: to help you in discovering of the formbuilder hidden structure we used the "border" attribute (the outcome doesn't follow the standard of beauty, but the example is very instructive!).
	
	When a formbuilder attribute begins with "lbl_" (like "lbl_width='10px'"), it means that EVERY "lbl" field attribute will be gain its properties. The same thing happens for each formbuilder attribute that begins with "fld_" (like "fld_width='10em'").