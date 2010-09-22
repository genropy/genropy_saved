# -*- coding: UTF-8 -*-

# formbuilder.py
# Created by Niso on 2010-09-20.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Formbuilder"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
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
    	| ``dbtable``        | See dbtable_ explanation                        |  ``None``                |
    	+--------------------+-------------------------------------------------+--------------------------+
    	| ``disabled``       | If True, user can't write in the form.          |  ``False``               |
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

    Here we describe the formbuilder's field attributes:

    	+----------------+------------------------------------------------------+--------------------------+
    	|   Attribute    |       Description                                    |   default                |
    	+================+======================================================+==========================+
    	| ``colspan``    | Set the number of columns occupied by a single field |  ``None``                |
    	+----------------+------------------------------------------------------+--------------------------+
    	| ``lbl``        | Set field label                                      |  ``None``                |
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

    	For further details on "dbtable" attribute, see #NISO METTERE IL LINK AL FILE DI DOCUMENTAZIONE SUL FIELD!!
    	
    """
    
    #   - Other forms and attributes:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to formbuilder.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##      --> ## file ##
    #       action          --> button.py
    #       button          --> button.py
    #       dateTextbox     --> textbox.py
    #       filteringSelect --> filteringSelect.py
    #       numberTextbox   --> textbox.py
    #       textbox         --> textbox.py
    #       value           --> datapath.py
    #       values          --> filteringSelect.py
    
    def test_1_basic(self,pane):
        """Standard formbuilder"""
        pane.div("""Since we haven't changed any of the default attributes of the formbuilder,
                the fields are stacked on a single column, have a dimension of '7em' and
                have a space of 6 pixels between fields themselves.
                In test_3 we'll make some changes of formbuilder default attributes.""",
                font_size='.9em',text_align='justify')
        fb = pane.formbuilder(datapath='test1')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',lbl='Surname')
    def test_2_structure(self,pane):
        """Formbuilder structure"""
        pane.div("""Every formbuilder column is splitted in two parts (left one and right one):
                the right part is the one where user can compile fields, while the left part
                is where "lbl" attribute appear. You can also see the effect of
                "border_spacing" css attribute, that is the space between fields.
                Last thing: to help you in discovering of the formbuilder hidden structure
                we used the "border" attribute (the outcome doesn't follow the standard of
                beauty, but the example is very instructive!).""",
                font_size='.9em',text_align='justify')
        fb = pane.formbuilder(datapath='test2',border='5px')
        fb.button('Click here',action="alert('Clicked!')",lbl='A button')
        fb.textbox(value='^.name',lbl='Name')
        
    def test_3_attributes(self,pane):
        """Formbuilder attributes"""
        pane.div("""When a formbuilder attribute begins with "lbl_" (like "lbl_width='10px'"),
                it means that EVERY "lbl" field attribute will be gain its properties.
                The same thing happens for each formbuilder attribute that begins with
                "fld_" (like "fld_width='10em'").""",
                font_size='.9em',text_align='justify')
        pane.div("""To create a beautiful form, we suggest you to write "fld_width='100%'"
                and "width='100%'" as formbuilder attributes.""",
                font_size='.9em',text_align='justify')
        pane.div(""" "cols" set the number of columns of the formbuilder. If you set cols=2
                and create 3 fields, they will be placed into two columns like this:""",
                font_size='.9em',text_align='justify')
        pane.span("field_1 ",font_size='.9em',text_align='justify')
        pane.span("field_2",font_size='.9em',text_align='justify')
        pane.div("field_3",font_size='.9em',text_align='justify')
        pane.div("Setting \"cols=3\" would have led to this result, as we expected in an HTML table:",
                font_size='.9em',text_align='justify')
        pane.span("field_1 field_2 field_3",font_size='.9em',text_align='justify')
        pane.div("""With "colspan" you can fullfil with a single field the space of two or more
                field (for an example check the textbox with 'lbl=Surname')""",
                font_size='.9em',text_align='justify')
        pane.div("\"fld_width\" set the dimension of every field.",
                font_size='.9em',text_align='justify')
                
        fb=pane.formbuilder(datapath='test3',cols=3,fld_width='100%',width='100%',lbl_color='red')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',colspan=2,lbl='Surname')
        fb.numberTextbox(value='^.age',lbl="Age")
        fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
        fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
        fb.textbox(value='^.job.profession',lbl='Job')
        fb.textbox(value='^.job.company_name',lbl='Company name')
        fb.textbox(value='^.job.fiscal_code',lbl='Fiscal code')
        
    def test_4_disabled(self,pane):
        """Disabled"""
        pane.div("""In this test you can see the effect of the "disabled" formbuilder attribute: if True
                    user can't write in the form (use the checkbox to activate this attribute).""",
                font_size='.9em',text_align='justify')
        fb=pane.formbuilder(datapath='test5',cols=3,fld_width='100%',width='100%',disabled='^disab')
        fb.checkbox(value='^disab',lbl='form DISABLED',lbl_width='8em')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',lbl='Surname')
        fb.numberTextbox(value='^.age',lbl="Age")
        fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
        fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
        fb.textbox(value='^.job.profession',lbl='Job')
        fb.textbox(value='^.job.company_name',lbl='Company name')
        
# This is a bad test to correct the lblpos and lblalign functioning...
    def test_5_pos_align(self,pane):
        """lblpos and lblalign"""
        pane.div('lblpos = \'L\' ')
        fb = pane.formbuilder(cols=2,lblpos='L')
        fb.textbox(value='^top',lbl='left')
        fb.textbox(value='^top2',lbl='left')
        fb.textbox(value='^top3',lbl='left')
        fb.textbox(value='^top4',lbl='left')
        
        pane.div('lblpos = \'T\' ')
        fb = pane.formbuilder(cols=2,lblpos='T')
        fb.textbox(value='^top',lbl='top')
        fb.textbox(value='^top2',lbl='top')
        fb.textbox(value='^top3',lbl='top')
        fb.textbox(value='^top4',lbl='top')
        
        pane.div('lblalign = \'left\' ')
        fb = pane.formbuilder(cols=2,lblpos='T',lblalign='left')
        fb.textbox(value='^top',lbl='left')
        fb.textbox(value='^top2',lbl='left')
        fb.textbox(value='^top3',lbl='left')
        fb.textbox(value='^top4',lbl='left')
        
        pane.div('lblalign = \'right\' ')
        fb = pane.formbuilder(cols=2,lblpos='T',lblalign='right')
        fb.textbox(value='^top',lbl='right')
        fb.textbox(value='^top2',lbl='right')
        fb.textbox(value='^top3',lbl='right')
        fb.textbox(value='^top4',lbl='right')
        