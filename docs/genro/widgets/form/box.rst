=====
 Box
=====

.. currentmodule:: form

.. class:: Boxes -  Genropy boxes

	We now introduce textbox, number textbox, date textbox, time textbox, currency textbox,
    simple textarea, number spinner. They are form widgets inherit from Dojo.
    
    - common box attributes:

		+-----------------------+---------------------------------------------------------+-------------+
		|   Attribute           |          Description                                    |   Default   |
		+=======================+=========================================================+=============+
		| ``font_size``         | CSS attribute                                           |  ``1em``    |
		+-----------------------+---------------------------------------------------------+-------------+
		| ``text_align``        | CSS attribute                                           |  ``left``   |
		+-----------------------+---------------------------------------------------------+-------------+
		| ``default``           | Add the default box value (use a default type supported |  ``None``   |
		|                       | from your box!). It's not compatible with dateTextbox   |             |
		|                       | and timeTextbox                                         |             |
		+-----------------------+---------------------------------------------------------+-------------+
        
    - Boxes:

        - textbox: a simple textbox.

			Example::
			
				pane.textbox('Hello world!')
            
        - currencyTextbox: it inherit all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.

		+------------------------+-------------------------------------------------------+-------------+
		|   Attribute            |          Description                                  |   Default   |
		+========================+=======================================================+=============+
		| ``text_align``         | CSS attribute                                         |  ``right``  |
		+------------------------+-------------------------------------------------------+-------------+
		| ``currency``           | specify used currency                                 |  ``None``   |
		+------------------------+-------------------------------------------------------+-------------+
		| ``locale``             | specify currency format type                          |  ``it``     |
		+------------------------+-------------------------------------------------------+-------------+
		
		Example::
		
			pane.currencyTextBox(value='^.amount',default=1123.34,currency='EUR',locale='it')
        
        - dateTextbox: it's a easy-to-use date entry controls that allow either typing or choosing a date from any calendar widget.

        - sintax: GG/MM/AAAA

		+------------------------+-------------------------------------------------------+-------------+
		|   Attribute            |          Description                                  |   Default   |
		+========================+=======================================================+=============+
		| ``popup``              | allow to show a calendar dialog.                      |  ``True``   |
		+------------------------+-------------------------------------------------------+-------------+
        
		example::
		
			pane.dateTextbox(value='^.dateTextbox')
        
        - numberTextbox: a simple number textbox.

            - attributes:
                places=3    (if is reached the fourth decimal, a tooltip error will warn user.)
                text_align='right'
                
        - numberSpinner: it's similar to numberTextBox, but makes integer entry easier when
                         small adjustments are required.

						There are two features:
						
                         - The down and up arrow buttons "spin" the number up and down.
                         - Furthermore, when you hold down the buttons, the spinning accelerates to make coarser adjustments easier.

				+----------------+---------------------------------+-------------+
				|   Attribute    |          Description            |   Default   |
				+================+=================================+=============+
				| ``min=NUMBER`` | set min value of numberSpinner. |  ``None``   |
				+----------------+---------------------------------+-------------+
				| ``max=NUMBER`` | set max value of numberSpinner. |  ``None``   |
				+----------------+---------------------------------+-------------+
                
        - simpleTextarea: a simple text area.
            
        - timeTextbox: it's a time input control that allow either typing time or choosing it from
                       a picker widget.

            - sintax: HH:MM
