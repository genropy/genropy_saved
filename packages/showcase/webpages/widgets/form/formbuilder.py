# -*- coding: UTF-8 -*-

# formbuilder.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Formbuilder"""

class GnrCustomWebPage(object):
    
    """ With formbuilder you have an ordered place to put your HTML object;
    formbuilder is used in place of an HTML table.
    To let you see how Genro code is simpler and more compact, we report here
    a comparison between an HTML table and a Genro formbuilder.
    
    HTML code:
    table = root.table()
    row = table.tr()
    row.td('Nome')
    row.td().textbox(value='^nome')
    
    Genro code:
    fb = root.formbuilder()
    fb.textbox(value='^nome',lbl='Nome')
    
    In formbuilder you can put dom and widget elements; its most classic usage is to create
    a form made by fields and layers, and that's because formbuilder can manage automatically
    fields and their positioning.
    
    - formbuilder's attributes (and default values)
        border_spacing (6px)
        cols: set columns number (1)
        fld_width: set field width (7em)
        pos: choose element position;       Sintax: pos(number,number)
                                                whereas the first value represents a row, the second
                                                value represents a column.
                                            Default: the element is positioned into the first free position.
                                            Other feature: pos can accept as a number row two special characters:
                                            + to refer itself at the following row
                                            * to refer itself at the current row
        
    - formbuilder's fields attributes:
        lbl: set label.
        lblclass: set label style.
        lblpos: set label position.
        lblalign: set label alignment. """
    
    #   - Other forms and attributes:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to formbuilder.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##      --> ## file ##
    #       action          --> button.py
    #       button          --> button.py
    #       datapath        --> datapath.py
    #       dateTextbox     --> textbox.py
    #       filteringSelect --> filteringSelect.py
    #       numberTextbox   --> textbox.py
    #       textbox         --> textbox.py
    #       value           --> datapath.py
    #       values          --> filteringSelect.py
    
    py_requires="gnrcomponents/testhandler:TestHandlerBase"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """Standard formbuilder"""
        pane.div("""Since we haven't changed any of the default attributes of the formbuilder,
                the fields are stacked on a single column, have a dimension of '7em' and
                have a space of 6 pixels between fields themselves.
                In test_3 we'll make some changes of formbuilder default attributes.""",
                font_size='.9em',text_align='justify')
        fb = pane.formbuilder(datapath='test1')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(lbl='Surname')
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
        fb = pane.formbuilder(border='5px')
        fb.button('Click here',action="alert('Clicked!')",lbl='A button')
        fb.textbox(lbl='Name')
        
    def test_3_attributes(self,pane):
        """Formbuilder attributes"""
        pane.div("""When a formbuilder attribute begins with "lbl_" (like "lbl_width='10px'"),
                it means that EVERY "lbl" field attribute will be gain its properties.
                The same thing happens for each formbuilder attribute that begins with
                "fld_" (like "fld_width='10em'").
                To create a beautiful form, we suggest you to write "fld_width='100%'"
                and "width='100%'" as formbuilder attributes.
                "cols" set the number of columns of the formbuilder. If you set cols=2
                and create 3 fields, they will be placed into two columns like this:
                field_1         field_2
                field_3
                Setting "cols=3" would have led to this result, as we expected in an HTML table:
                field_1         field_2        field_3
                With "colspan" you can fullfil with a single field the space of two or more
                field (for an example see in test_3 the textbox with 'lbl=Surname', where)
                "fld_width" set the dimension of every field; if you want to change a single
                field you have to use the attribute "field" on it.
                There are also some attributes that doesn't strictly belong to formbuilder
                (like "datapath", etc): see paragraph "Other forms and attributes" for more details.""",
                font_size='.9em',text_align='justify')
        fb=pane.formbuilder(cols=3,fld_width='100%',width='100%',lbl_color='red',datapath='employee')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',colspan=2,lbl='Surname')
        fb.numberTextbox(value='^.age',lbl="Age")
        fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
        fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
        fb.textbox(value='^.job.profession',lbl='Job')
        fb.textbox(value='^.job.company_name',lbl='Company name')
        fb.textbox(value='^.job.fiscal_code',lbl='Fiscal code')
        