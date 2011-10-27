.. _relation_attrs:

========================================
relation method - attributes explanation
========================================
    
    *Last page update*: |today|
    
    * :ref:`group`
    * :ref:`one_one`
    * :ref:`one_name`
    
.. _relation_intro:

introduction
============

    In this page we give examples of all the features of the :ref:`table_relation`

.. _group:

group
=====

    **definition and description**:

    The *group* attribute allow to order the :ref:`columns <column>` in the Search Box of the
    action bar of the :ref:`th` component. For more information on the location of the Search Box,
    please check the :ref:`th_search_box` section.
    
    CLIPBOARD::
    
        there are two syntaxes for it
        
        1. firstly you can use it . . to change the order of the field list
        this way requires only an alphanumeric code
        and the fields ordered by this code
        
        2 group='_'
        means invisible
        
        3. The group attribute can be used to enclose the columns in a branch of the fields tree
        for this to work . . let me give you an example . .
        
        when defining the pkg.table we can include attributes
        group_suffix
        so for example:
        
        group_a_names='Names and Codes',
        group_b_addresses='Addresses',
        group_c_communications='Communications',
        
        the suffix will be how the group branch is ordered
        and the ='Names and Code'
        as an example . . is the name of the group
        
        now to use this group in a column attribute we would do the following :
        tbl.aliasColumn('name_all', relation_path='@card_id.name_all', name_long='!!All names',group='a_names.5')
        tbl.aliasColumn('name_full', relation_path='@card_id.name_full', name_long='!!Full name',group='a_names.10')
        tbl.aliasColumn('name_last', relation_path='@card_id.name_last', group='a_names.20')
        so the group equals the suffix defined in pkg.tbl
        and we can add a further suffix (.10)
        so order the columns within that group
        
        so, the '.10' introduce a subgroup?
        an order for the defined column within the group branch
        
        but the dot in '.10' is a predefined syntax? Or one can use '_10' ?
        it is a convention
        but you can use anything
        mmm actually no the dot is required
        so
        ``group_groupname.order``

    You may use some special characters:

    * if the group path starts with ``_``, then the group is "reserved" (invisible)
    * if it starts with ``*`` it can be seen only through administration tools (add???)

    **validity**:

    The *group* attribute works on:

    * table :ref:`columns <column>`
    * the :ref:`sysfields` and the :ref:`set_tagcolumn` methods (a method of the
      :class:`gnr.app.gnrdbo.TableBase` class)

.. _one_one:

one_one
=======

    CLIPBOARD::
    
        one_one=True    specifico che è una one_one. se non lo metto
                        la relazione è una a molti!
        one_one='*'     magia! crea il relation_name (cioè come path di relazione inverso)
                        con nome uguale a nome della table ()
                        
.. _one_name:

one_name
========

    add???