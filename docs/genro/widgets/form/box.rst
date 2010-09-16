=====
 Box
=====

.. currentmodule:: form

.. class:: Boxes -  Genropy boxes

	We now introduce textbox, number textbox, date textbox, time textbox, currency textbox,
    simple textarea, number spinner. They are form widgets inherit from Dojo.
    
    - common default values of box attributes:
        
        ``font_size='1em'``
        
        ``text_align='left'``
        
    Here we introduce the attributes belonging to every box:
        default='VALUE' Add a default value in your box (use a type supported from your box!).
                        It's not compatible with dateTextbox and timeTextbox.
        
    - Boxes: 
        - textbox: a simple textbox.
            
        - currencyTextbox: it inherit all the attributes and behaviors of the numberTextbox widget
                           but are specialized for input monetary values, much like the currency type
                           in spreadsheet programs.
            - attributes:
                text_align='right'
                
        - dateTextbox: it's a easy-to-use date entry controls that allow either typing or choosing a date
                       from any calendar widget.
            - sintax: GG/MM/AAAA
            - attributes:
                popup=True  allow to show a calendar dialog.
                
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
