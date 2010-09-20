=============
 formbuilder
=============

.. currentmodule:: form

.. class:: formbuilder -  Genropy formbuilder

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
	
	Definition::
	
		def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
	                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
	                    lblalign=None, lblvalign='middle',
	                    fldalign=None, fldvalign='middle',disabled=False,
	                    rowdatapath=None, head_rows=None, **kwargs):

In formbuilder you can put dom and widget elements; its most classic usage is to create a form made by fields and layers, and that's because formbuilder can manage automatically fields and their positioning:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``border_spacing`` | CSS attribute, space between rows               |  ``6px``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``cols``           | Set columns number                              |  ``1``                   |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``fld_width``      | Set field width                                 |  ``7em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``pos``            | Choose element position                         |  The first free position |
	|                    |                                                 |                          |
	|                    | Sintax: pos(NUMBER,NUMBER)                      |                          |
	|                    |     whereas the first value represents a row,   |                          |
	|                    |                                                 |                          |
	|                    |     the second value represents a column.       |                          |
	|                    |                                                 |                          |
	|                    | Other feature: "pos" accepts as a number row    |                          |
	|                    |                                                 |                          |
	|                    | two special characters:                         |                          |
	|                    |                                                 |                          |
	|                    |         \+ to refer itself at the following row |                          |
	|                    |                                                 |                          |
	|                    |         \* to refer itself at the current row   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
Here we describe the formbuilder's field attributes:
	
	+----------------+-------------------------------------------------+
	|   Attribute    |       Values and description                    |
	+================+====================================+=============+
	| ``lbl``        | Set field label                    |  ``None``   |
	+----------------+------------------------------------+-------------+
	| ``lblclass``   | Set label style                    |  ``BOH``    |
	+----------------+------------------------------------+-------------+
	| ``lblpos``     | Set label position                               |
	|                |                                                  |
	                   ``L`` (default):
	                   ``T`` :
	+----------------+------------------------------------+-------------+
	| ``lblalign``   | Set label alignment                |  ``BOH``    |
	+----------------+------------------------------------+-------------+
	