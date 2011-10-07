.. _th_map:

===================
TableHandler: paths
===================
    
    *Last page update*: |today|
    
    * :ref:`th_map`:
    
        * :ref:`th_map_structure`
        * :ref:`th_map_data`
        
        * :ref:`th_map_selectedpage`
        * :ref:`th_map_form`
        * :ref:`th_map_view`
        
.. _th_map_intro:

TableHandler: paths
===================

    In this section you will learn about the path structure of the TableHandler
    
    As any other object in Genro, the TableHandler gathers all the informations through
    a :ref:`bag` structure, that looks like a hierarchical and nested structure. Also,
    every TableHandler is a macrocomponent including different logical entities. So,
    after you defined it you can (and often it is recommended!) modify some parts of
    the TableHandler. To access to its parts, you have to use the TableHandler paths
    
    What you should know is a complete map of the TableHandler path levels: in particular
    we can divide them in:
    
    * :ref:`th_map_structure`
    * :ref:`th_map_data`
    
.. _th_map_structure:

TableHandler structure levels
=============================

    Let's see the TableHandler structure levels:
    
    * the base level is the ``th`` level
    * inside the th level there are two (or three) main levels that are:
    
        * the :ref:`th_map_form` (``.form``) that handles the :ref:`th_form_class` content
        * the :ref:`th_map_view` (``.view``) that handles the :ref:`th_view_class` content
        * eventually the :ref:`th_map_selectedpage` (this level exists only if you use the :ref:`th_stack`)
        
    Inside the form level and the view level there are other sublevels that we describe later.
    For now just check the following image to have a overview of the TableHandler structure:
      
    .. image:: ../../../_images/components/th/path.png
    
    Examples of TableHandler paths:
    
    * to reach the top level of the view level, you have to use this string::
    
        th.view.top
        
    * to reach the bar level of the bottom level of the form level, you have to use
      this string::
    
        th.form.bottom.bar
        
.. _th_map_data:

TableHandler data levels
========================
    
    To access to data you have to know that the root level of TableHandler data is::
    
        packageName_tableName
        
    where:
    
    * ``packageName`` is the name of your :ref:`package <packages>`
    * ``tableName`` is the name of your :ref:`table`
    
    .. image:: ../../../_images/components/th/path_data.png
    
    In particular:
    
    * at the path ``packageName_tableName.form.record`` you can find the data handled
      by the :ref:`th_form_class`
      
    .. note:: Remember that you can inspect the path of data directly on your browser
              by opening the :ref:`datastore_debugger`
              
.. _th_map_form:

form level
----------

    This level handles all the data of the :ref:`th_form_class`
    
    It has got two level categories:
    
    * the :ref:`structure levels <th_map_form_layout>`
    * the :ref:`data levels <th_map_form_data>`
    
.. _th_map_form_layout:

form - structure levels
-----------------------

    At the ``th/form`` level, the path of the data is::
    
        .packageName_tableName.form
        
    The inner gears of the ``form`` level are built in complete analogy with
    the structure of a Dojo :ref:`bordercontainer`, so this level includes
    five region-paths:
    
    * ``top``: it includes the title of the view page [#]_ and the :ref:`workdate`.
    
      (The ``top`` level has a ``bar`` sublevel: this sublevel contains
        some query tools and some buttons to add or delete records.)
    * ``bottom``: it is thought to give to user messages (e.g: 'Save OK').
    
      (The ``bottom`` level have an additional ``bar`` level.)
    * ``left``: it allows the user to perform some useful action (e.g: to configurate
        user view; e.g: to export query results in a ``.xls`` file).
    * ``right``: it is empty.
    * ``center``: it is the space in which you build a GUI to let the user create and
      modify records. We'll come back later to it, in the :ref:`th_form_center_path`
      section.
      
.. _th_map_form_data:

form - data levels
------------------

    In the form level you can find four data levels:
    
    * **controller**: it contains many levels that allow to control the save/load management,
      the incorrect fields and so on (you can check all of them by activating the
      :ref:`datastore_debugger`)
      
      We point up the following levels:
      
      * **invalidFields**: string. If some field is uncorrect (that is, it doesn't satisfy a
          :ref:`validation <validations>`) it contains the path of that field::
          
              packageName_tableName_form_record_columnName
              
          where ``packageName`` is the name of the package, ``tableName`` is the name of the table
          and ``columnName`` is the name of the uncorrect column
          
      * **table**: string. It includes the name of the package and the name of the table following
        this syntax::
        
            packageName.tableName
            
      * **title**: string. It includes the name of the record title in the :ref:`data_entry`
      * **valid**: boolean, string. True if every :ref:`validation <validations>` is satisfied
      
    * **handler**: add???
    * **record**: this level contains all the :ref:`columns <column>` of your :ref:`table`
      
      At the ``th/form/record`` level, the path of the data is::
        
        .packageName_tableName.form.record
        
      .. warning:: at this path level you find the records data, so remember that when you
                   have to interact with data you have to go to the ``form.record`` path
                   
    * **pkey**: this level contains:
    
        * the ``*newrecord*`` string - if no record is selected
        * the string with the primary key of the selected record - if a record is selected
        
.. _th_map_view:

view level
----------

    The view level contains many levels. We point up the following ones:
    
    * **grid**: add???
    * **query**: it contains the parameters of the user queries
    * **store**: it contains all the records that satisfy the current query
    * **table**: it includes the name of the package and the name of the table
      following this syntax::
        
            packageName.tableName
            
    * **title**: it contains the name of the record title in the :ref:`view_data`
    * **top**: it includes a ``bar`` sublevel: this sublevel contains the
      :ref:`th_gui_form_action_bar`. If you need to add/replace/delete some buttons, use the
      :meth:`replaceSlots() <gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.slotbar_replaceslots>` method
      
      ::
      
        th.view.top.bar.replaceSlots('#','#,my_button')
        th.view.top.bar.my_button.button('New print',action='PUBLISH tablehandler_run_script="print","performances_print";')
        
.. _th_map_selectedpage:

selectedPage level
------------------

    The selectedPage path exists only if you use the :ref:`th_stack`.
    
    The selectedPage contains:
    
    * *form*, if the selected page is the :ref:`view_data`
    * *view*, if the selected page is the :ref:`data_entry`
    
**Footnotes**:

.. [#] The title of the view page is taken from the :ref:`name_long` of the :ref:`table` to which the current webpage refers to.
.. [#] The :ref:`formbuilder` allows to create in a simple way a :ref:`form`. Follow the links for more information.
.. [#] We remember you that the name of the ``th_webpage`` can be the one you prefer, but as a convention we suggest you to call it with ``name of table`` + ``_page`` suffix.
