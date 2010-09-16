# -*- coding: UTF-8 -*-

# box.py
# Created by Niso on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Box"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
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

    		+------------------------+-------------------------------------------------------+-------------+
    		|   Attribute            |          Description                                  |   Default   |
    		+========================+=======================================================+=============+
    		| ``places``             | Numbers of decimals. If it's reached the last         |  ``3``      |
    		|                        | supported decimal, a tooltip error will warn user.    |             |
    		+------------------------+-------------------------------------------------------+-------------+
    		| ``text_align``         | CSS attribute                                         |  ``right``  |
    		+------------------------+-------------------------------------------------------+-------------+

    		example::

    			pane.numberTextbox(value='^.numberTextbox',places=2)

            - numberSpinner: it's similar to numberTextBox, but makes integer entry easier when
                             small adjustments are required.

    						There are two features:

                             - The down and up arrow buttons "spin" the number up and down.
                             - Furthermore, when you hold down the buttons, the spinning accelerates to make coarser adjustments easier.

    		+----------------+---------------------------------------------------------------+-------------+
    		|   Attribute    |          Description                                          |   Default   |
    		+================+===============================================================+=============+
    		| ``min=NUMBER`` | set min value of numberSpinner.                               |  ``None``   |
    		+----------------+---------------------------------------------------------------+-------------+
    		| ``max=NUMBER`` | set max value of numberSpinner.                               |  ``None``   |
    		+----------------+---------------------------------------------------------------+-------------+

    		example::

    			pane.numberSpinner(value='^.age',default=100,min=0)

            - simpleTextarea: a simple text area.

    		example::

    			pane.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
    	                            colspan=2,color='blue',font_size='1.2em',
    	                            default='A simple area to contain text.')

            - timeTextbox: it's a time input control that allow either typing time or choosing it from
                           a picker widget.

    		- sintax: HH:MM

    		example::

    			pane.timeTextBox(value='^.timeTextbox')
        """
        
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to boxes.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       datapath            --> webpages/tutorial/datapath.py
    #       formbuilder         --> formbuilder.py
    #       nodeId              --> form.py
    #       validate_len        --> form.py
    #       validate_onAccept   --> form.py
    #       validate_onReject   --> form.py
    #       value               --> webpages/tutorial/datapath.py
    
    def test_1_textbox(self,pane):
        """Textbox"""
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.textBox(value='^.textBox',default='ciao')
        fb.div("A simple textbox.",font_size='.9em',text_align='justify')
        fb.textBox(value='^.textBox_2',nodeId='name',
                   validate_len='4:',
                   validate_onReject='alert(value+" is too short (minimum 4 characters)")',
                   validate_onAccept='alert("Correct lenght of "+value)')
        fb.div(""" A textbox with "validate" attributes. Here you have to write a text
                   with 4 or more characters.""",
                   font_size='.9em',text_align='justify')
                   
    def test_2_numberTextbox(self,pane):
        """numberTextbox"""
        fb = pane.formbuilder(datapath='test2',cols=2)
        fb.numberTextBox(value='^.numberTextbox')
        fb.div("""A simple number textbox. You can write any number with no more than three 
                decimals.""",font_size='.9em',text_align='justify')
        fb.numberTextbox(value='^.numberTextbox_2',places=3)
        fb.div("With \"places=3\" you must write a number with three decimals.",
                   font_size='.9em',text_align='justify')
                   
    def test_3_numberSpinner(self,pane):
        """numberSpinner"""
        fb = pane.formbuilder(datapath='test3',cols=2)
        fb.numberSpinner(value='^.age',default=100,min=0)
        fb.div("""Try to hold down a button: the spinning accelerates
                    to make coarser adjustments easier""",
                   font_size='.9em',text_align='justify',margin='5px')
                   
    def test_4_simpleTextarea(self,pane):
        """simpleTextarea"""
        fb = pane.formbuilder(datapath='test4')
        fb.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
                            colspan=2,color='blue',font_size='1.2em',
                            default='A simple area to contain text.')
                            
    def test_5_dateTextbox(self,pane):
        """dateTextbox"""
        fb = pane.formbuilder(datapath='test5')
        fb.dateTextbox(value='^.dateTextbox')
        
    def test_6_timeTextbox(self,pane):
        """timeTextbox"""
        fb = pane.formbuilder(datapath='test6')
        fb.timeTextBox(value='^.timeTextbox')
        
    def test_7_currencyTextbox(self,pane):
        """currencyTextbox"""
        fb = pane.formbuilder(datapath='test7')
        fb.currencyTextBox(value='^.amount',default=1123.34,currency='EUR',locale='it')
        
    def test_8_mixed(self,pane):
        """Mixed"""
        fb = pane.formbuilder(datapath='test8',cols=3,fld_width='100%',width='100%')
        fb.textBox(value='^.r0.name',lbl='Name')
        fb.textBox(value='^.r0.surname',lbl='Surname',colspan=2)
        fb.dateTextBox(value='^.r0.birthday',lbl='Birthday')
        fb.dateTextBox(value='^.r0.date',popup=False,lbl='Date (no popup)')
        fb.div('remember: date format is GG/MM/AAAA',
                font_size='.9em',text_align='justify')
        fb.numberTextBox(value='^.r0.age',lbl='Age')
        fb.textBox(value='^.r0.text',width='5em',lbl='Text')
        