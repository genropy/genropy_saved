==========================
:mod:`gnr.core.gnrbaghtml`
==========================
    
    *Last page update*: |today|
    
    **Classes**:
    
    * :ref:`gnrbaghtml_bagtohtml`
    * :ref:`bagtohtml_webpage_variables`
    
    **Complete reference**:
        
    * :ref:`gnrbaghtml_classes`
    
.. _gnrbaghtml_bagtohtml:

:class:`BagToHtml`
==================

    .. module:: gnr.core.gnrbaghtml.BagToHtml
    
    ============================= ============================ ========================== ========================
    :meth:`calcDocFooterHeight`   :meth:`defineStandardStyles` :meth:`gridLayout`         :meth:`pageCounter`      
    :meth:`calcDocHeaderHeight`   :meth:`docFooter`            :meth:`init`               :meth:`pageFooter`      
    :meth:`calcGridFooterHeight`  :meth:`docHeader`            :meth:`initializeBuilder`  :meth:`pageHeader`      
    :meth:`calcGridHeaderHeight`  :meth:`field`                :meth:`main`               :meth:`prepareTemplates`
    :meth:`calcRowHeight`         :meth:`fillBodyGrid`         :meth:`mainLayout`         :meth:`rowCell`         
    :meth:`copyHeight`            :meth:`get_css_requires`     :meth:`mainLoop`           :meth:`rowField`        
    :meth:`copyValue`             :meth:`getData`              :meth:`onRecordExit`       :meth:`setData`         
    :meth:`copyWidth`             :meth:`getTemplates`         :meth:`onRecordLoaded`     :meth:`setTemplates`    
    :meth:`createHtml`            :meth:`gridFooter`           :meth:`orientation`        :meth:`showTemplate`    
    :meth:`defineCustomStyles`    :meth:`gridHeader`           :meth:`outputDocName`      :meth:`toText`          
    ============================= ============================ ========================== ========================
    
.. _bagtohtml_webpage_variables:

BagToHtml - webpage variables
=============================
    
    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize the class to which they belong (in this case, the
    BagToHtml class).
    
    .. note:: the unit of measurement of all the numerical variables are in millimeters
              (e.g: ``print_width = 200`` means 200 millimeters)
              
    .. note:: the three levels in which is divided the print zone are:
    
              * the :ref:`print_layout_page` level
              * the :ref:`print_layout_doc` level
              * the :ref:`print_layout_grid` level
              
              Most of the following webpage variables are related to these three print zones;
              please check the :ref:`print_layout_pagedocgrid` section for more information
              about them
              
    The webpage variables are:
    
    * :ref:`bagtohtml_copies_per_page`       
    * :ref:`bagtohtml_copy_extra_height`     
    * :ref:`bagtohtml_css_requires`          
    * :ref:`bagtohtml_currencyformat`        
    * :ref:`bagtohtml_doc_header_height`     
    * :ref:`bagtohtml_doc_footer_height`     
    * :ref:`bagtohtml_encoding`              
    * :ref:`bagtohtml_grid_header_height`    
    * :ref:`bagtohtml_grid_footer_height`    
    * :ref:`bagtohtml_grid_col_headers`      
    * :ref:`bagtohtml_grid_col_widths`       
    * :ref:`bagtohtml_grid_row_height`       
    * :ref:`bagtohtml_page_debug`            
    * :ref:`bagtohtml_page_footer_height`    
    * :ref:`bagtohtml_page_header_height`    
    * :ref:`bagtohtml_page_height`           
    * :ref:`bagtohtml_page_width`            
    * :ref:`bagtohtml_page_leftbar_width`    
    * :ref:`bagtohtml_page_rightbar_width`   
    * :ref:`bagtohtml_page_margin_bottom`    
    * :ref:`bagtohtml_page_margin_left`      
    * :ref:`bagtohtml_page_margin_right`     
    * :ref:`bagtohtml_page_margin_top`       
    * :ref:`bagtohtml_print_button`          
    * :ref:`bagtohtml_row_mode`              
    * :ref:`bagtohtml_rows_path`             
    * :ref:`bagtohtml_starting_page_number`  
    * :ref:`bagtohtml_templates`             
    
.. _bagtohtml_copies_per_page:

copies_per_page
---------------

    add???. Default value is ``1``
    
.. _bagtohtml_copy_extra_height:

copy_extra_height
-----------------

    add???. Default value is ``0``
    
.. _bagtohtml_css_requires:

css_requires
------------

    Set the css files to import. Default value is ``''`` (empty string)
    
        **Example**::
        
            css_requires = 'my_style'
            
        This line implies that you have created a CSS file called ``my_style.css``
        
    .. note:: The CSS files you want to use must be placed into your "``resources``" folder
              
              * For more information about Genro CSS, please check the :ref:`css` page.
              * For more information about their location in a Genro :ref:`project`,
                please check the :ref:`intro_resources` page.
                
.. _bagtohtml_currencyformat:

currencyFormat
--------------

    Set the :ref:`table_format` of the numerical columns of the print.
    Default value is ``u'#,###.00'``
    
.. _bagtohtml_doc_header_height:

doc_header_height
-----------------

    Set the height of the :ref:`print_layout_doc` header in millimeters.
    Default value is ``0``.
    
    .. note:: you can call the :ref:`layout_docheader` method only if you
              give a different dimension respect to ``0`` to this attribute
              
.. _bagtohtml_doc_footer_height:

doc_footer_height
-----------------

    Set the footer of the :ref:`print_layout_doc` footer in millimeters.
    Default value is ``0``
    
    .. note:: you can call the :ref:`layout_docfooter` method only if you
              give a different dimension respect to ``0`` to this attribute
              
.. _bagtohtml_encoding:

encoding
--------

    Set the encoding of your data. Default value is ``'utf-8'``
    
.. _bagtohtml_grid_header_height:

grid_header_height
------------------

    Set the height of the :ref:`print_layout_grid` header in millimeters.
    Default value is ``0``
    
.. _bagtohtml_grid_footer_height:

grid_footer_height
------------------

    Set the height of the :ref:`print_layout_grid` footer in millimeters.
    Default value is ``0``
    
.. _bagtohtml_grid_col_headers:

grid_col_headers
----------------

    String. Set the header names of the print columns. Default value is ``None``
    
.. _bagtohtml_grid_col_widths:

grid_col_widths
---------------

    List. Set the width of the :ref:`print_layout_grid` columns in millimeters.
    Default value is ``[0, 0, 0]``
    
    .. note:: Every column you set equal to ``0`` takes the remaining place divided equally
    
    **Example**::
    
        grid_col_widths = [0,0,0]
        
    in this example we have 3 columns that get the current grid width divided
    equally in 3
    
    **Example**::
    
        grid_col_widths = [17,12,0,0,20,15,15,20]
        
    in this example we have 8 columns; the first one measures 17 mm, the second
    one 12 mm and so on. The total millimeters specified are 99 (17+12+20+15+15+20),
    so if we suppose that the total width of the grid is 149 millimeters, then the
    remaining space (that is: 149 - 99 = 50 millimeters) will be taken from the
    third and the fourth columns divided equally (both the third and the fourth
    columns have a width of 50:2 = 25 millimeters)
    
.. _bagtohtml_grid_row_height:

grid_row_height
---------------

    Set the height of the :ref:`print_layout_grid` rows in millimeters. Default value
    is ``5``
    
        **Example**::
        
            grid_row_height = 5.3
            
.. _bagtohtml_page_debug:

page_debug
----------

    boolean. add??? Default value is ``False``
    
.. _bagtohtml_page_footer_height:

page_footer_height
------------------

    Set the :ref:`print_layout_page` footer height in millimeters.
    Default value is ``0``
    
    .. note:: you can call the :ref:`layout_pagefooter` method only if you
              give a different dimension respect to ``0`` to this attribute
              
.. _bagtohtml_page_header_height:

page_header_height
------------------

    Set the :ref:`print_layout_page` header height in millimeters.
    Default value is ``0``
    
    .. note:: you can call the :ref:`layout_pageheader` method only if you
              give a different dimension respect to ``0`` to this attribute
              
.. _bagtohtml_page_height:

page_height
-----------

    Set the :ref:`print_layout_page` height in millimeters.
    Default value is ``280``
    
.. _bagtohtml_page_leftbar_width:

page_leftbar_width
------------------

    Set the width of the :ref:`print_layout_page` left bar in millimeters
    Default value is ``0``
    
.. _bagtohtml_page_margin_bottom:

page_margin_bottom
------------------

    Set the :ref:`print_layout_page` bottom margin in millimeters.
    Default value is ``0``
    
.. _bagtohtml_page_margin_left:

page_margin_left
----------------

    Set the :ref:`print_layout_page` left margin in millimeters.
    Default value is ``0``
    
.. _bagtohtml_page_margin_right:

page_margin_right
-----------------

    Set the :ref:`print_layout_page` right margin in millimeters.
    Default value is ``0``
    
.. _bagtohtml_page_margin_top:

page_margin_top
---------------

    Set the :ref:`print_layout_page` top margin in millimeters.
    Default value is ``0``
    
.. _bagtohtml_page_rightbar_width:

page_rightbar_width
-------------------

    Set the width of the :ref:`print_layout_page` right bar in millimeters.
    Default value is ``0``
    
.. _bagtohtml_page_width:

page_width
----------

    Set the :ref:`print_layout_page` width in millimeters.
    Default value is ``200``
    
.. _bagtohtml_print_button:

print_button
------------

    add???. Default value is ``None``
    
.. _bagtohtml_row_mode:

row_mode
--------

    add???. You can set it to:
    
    * ``'value'``: (default value) add???
    * ``'attribute'``: add???
    
.. _bagtohtml_rows_path:

rows_path
---------
    
    add???. Default value is ``'rows'``
    
.. _bagtohtml_starting_page_number:

starting_page_number
--------------------

    Set the starting :ref:`print_layout_page` number. Default value is ``0``
    
.. _bagtohtml_templates:

templates
---------

    A string with the names of the :ref:`html templates <htmltemplate>` separated
    by a comma. More information in the :ref:`add???` section of the :ref:`htmltemplate`
    page
    
.. _gnrbaghtml_classes:

:mod:`gnr.core.gnrbaghtml` - The complete reference list
========================================================

.. automodule:: gnr.core.gnrbaghtml
    :members: