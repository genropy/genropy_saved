=============
 dateTextbox
=============

.. currentmodule:: form

.. class:: dateTextbox -  Genropy dateTextbox

    A dateTextbox is a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.
    
	- sintax: GG/MM/AAAA
	
	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``left``   |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``popup``             | allow to show a calendar dialog                         |  ``True``   |
	+-----------------------+---------------------------------------------------------+-------------+

		example::

			pane.dateTextbox(value='^dateTextbox',popup=True)