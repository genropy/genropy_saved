=============
 formbuilder
=============

.. currentmodule:: form

.. class:: formbuilder -  Genropy formbuilder

**Definition**::
	
		def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
	                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
	                    lblalign=None, lblvalign='middle',
	                    fldalign=None, fldvalign='middle', disabled=False,
	                    rowdatapath=None, head_rows=None, **kwargs):

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

In formbuilder you can put dom and widget elements; its most classic usage is to create a form made by fields and layers, and that's because formbuilder can manage automatically fields and their positioning:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``_class``         | For CSS style                                   |  `` ``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``border_spacing`` | CSS attribute, space between rows               |  ``6px``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``cols``           | Set columns number                              |  ``1``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``db_table``       | #NISO ???                                       |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | #NISO ???                                       |  ``False``               |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fieldclass``     | #NISO ??? Altri attributi!                      |  ``gnrfield``            |
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
	|                    |                                                 |                          |
	|                    | #NISO Sembra non funzionare                     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblclass``       | Set label style                                 |  ``gnrfieldlabel``       |
	|                    | #NISO Inserire possibili valori!                |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblpos``         | Set label position                              |  ``L``                   |
	|                    |                                                 |                          |
	|                    | ``L``: set label on the left side of text field |                          |
	|                    |                                                 |                          |
	|                    | ``T``: set label on top of text field           |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``lblvalign``      | Set vertical label alignment                    |  ``middle``              |
	|                    | #NISO Inserire possibili valori                 |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``pos``            | Choose element position                         |  The first free position |
	|                    |                                                 |                          |
	|                    | Sintax: pos(NUMBER,NUMBER)                      |                          |
	|                    |     whereas the first value represents a row,   |                          |
	|                    |     the second value represents a column.       |                          |
	|                    |                                                 |                          |
	|                    | Other feature: "pos" accepts as a number row    |                          |
	|                    | two special characters:                         |                          |
	|                    |                                                 |                          |
	|                    |         \+ to refer itself at the following row |                          |
	|                    |                                                 |                          |
	|                    |         \* to refer itself at the current row   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``rowdatapath``    | #NISO ???                                       |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``tblclass``       | The standard class for formbuilder.             |  ``formbuilder``         |
	|                    |                                                 |                          |
	|                    | Actually it is the unique defined class         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
	Example::
	
		pane.formbuilder(cols=2,border_spacing='10px',fld_width='100%')
	
Here we describe the formbuilder's field attributes:
	
	+----------------+--------------------------------------------------------+-------------+
	|   Attribute    |       Values and description                           |   default   |
	+================+========================================================+=============+
	| ``lbl``        | Set field label                                        |  ``None``   |
	+----------------+--------------------------------------------------------+-------------+
	
	Example::
	
		fb = pane.formbuilder(cols=2)
		fb.textbox(value='^name',lbl='Name')
	