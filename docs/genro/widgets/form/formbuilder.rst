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
    
In formbuilder you can put dom and widget elements; its most classic usage is to create
a form made by fields and layers, and that's because formbuilder can manage automatically
fields and their positioning.

    +--------------------+----------------------------------------------------------+-----------------------------------+
	|   Attribute        |          Description                                     |   Default                         |
	+====================+==========================================================+===================================+
	| ``border_spacing`` | If True, user can write in filteringSelect ignoring case |  ``True``                         |
	+--------------------+----------------------------------------------------------+-----------------------------------+
	| ``cols``           | Set columns number                                       |  ``1``                            |
	+--------------------+----------------------------------------------------------+-----------------------------------+
	| ``fld_width``      | Set field width                                          |  ``7em``                          |
	+--------------------+----------------------------------------------------------+-----------------------------------+
    | ``pos``            | Choose element position                                  |  ``The element is positioned into |
    |                    |                                                          |  the first free position ``       |
    |                    | Sintax: pos(NUMBER,NUMBER)                               |                                   |
    |                    |     whereas the first value represents a row, the second |                                   |
    |                    |     value represents a column.                           |                                   |
    |                    |     Other feature: "pos" accepts as a number row two     |                                   |
    |                    |         special characters:                              |                                   |
    |                    |         + to refer itself at the following row           |                                   |
    |                    |         * to refer itself at the current row             |                                   |
    +--------------------+----------------------------------------------------------+-----------------------------------+
    
Here we describe the formbuilder's field attributes:
    +--------------+---------------------+------------+
	|   Attribute  |  Description        |   Default  |
	+==============+=====================+============+
	| ``lbl``      | Set field label     |  ``None``  |
	+--------------+----------------------------------+
	| ``lblclass`` | Set label style     |  ``None``  |
	+--------------+----------------------------------+
    | ``lblpos``   | Set label position  |  ``Left``  |
	+--------------+----------------------------------+
    | ``lblalign`` | Set label alignment |  ``????``  |
	+--------------+---------------------+------------+