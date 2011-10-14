.. _th_gui:

=================
Tablehandler: GUI
=================

    *Last page update*: |today|
    
    * :ref:`th_gui_intro`
    * :ref:`view_data`:
    
        * :ref:`th_gui_view_top_bar`
        * :ref:`th_gui_view_action_bar`
        * :ref:`th_gui_central_pane`
        * :ref:`th_gui_view_bottom_bar`
        
    * :ref:`data_entry`:
    
        * :ref:`th_gui_form_top_bar`
        * :ref:`th_gui_form_action_bar`
        * :ref:`th_gui_form_box`
        * :ref:`th_gui_form_bottom_bar`
        
.. _th_gui_intro:

introduction
============

    In the following sections we discover the :ref:`th` GUI.
    
    Let's see this image:

    .. image:: ../../../_images/components/th/gui.png
    
    * The Tablehandler view class and form class take place into the central pane (point 2)
    * Points 1, 3 and 4 belong to the :ref:`frameindex` component
    
    The combination of a TableHandler in a :ref:`project` with the frameindex component is a good
    solution for having a quick pre-defined gui.
    
    However, in this page we'll talk about the view class and form class GUI, that is, the central
    pane (point 2). For more information on points 1, 3 and 4, please check the :ref:`frameindex` page.
    
.. _view_data:

view-data window
================

    The ``view-data window`` is the GUI of the TableHandler's :ref:`th_view_class`.
    
    It allows to:
    
    * visualize the records saved by the user
    * make a query to search into records
    
    Let's see this image:
    
    .. image:: ../../../_images/components/th/gui_view.png
    
    The view window has been divided through some colored box; in particular you can see:
    
    * the :ref:`th_gui_view_top_bar` (*red* box)
    * the :ref:`th_gui_view_action_bar` (*green* box)
    * the :ref:`th_gui_central_pane` (*blue* box)
    * the :ref:`th_gui_view_bottom_bar` (*yellow* box)
    
    In the next sub sections we explain in all the details these parts.
    
.. _th_gui_view_top_bar:

top bar
-------

    .. image:: ../../../_images/components/th/gui_view_topbar.png
    
    The top bar contains:
    
    #. the :meth:`windowTitle <gnr.web._gnrbasewebpage.GnrBaseWebPage.windowTitle>` method
    #. the :ref:`workdate`
    
.. _th_gui_view_action_bar:

action bar
----------

    .. image:: ../../../_images/components/th/GUI/view_actionbar/view_actionbar.png
    
    The action bar allow to perform many actions. In particular you can find:
    
    * the :ref:`th_search_box` (point 1)
    * the :ref:`th_query_bar` (points 2 and 3)
    * the :ref:`th_query_value` (point 4)
    * the :ref:`th_run_query_button` (point 5)
    * the :ref:`th_query_actions` (point 6)
    * the :ref:`th_query_result_numbers` (point 7)
    * the :ref:`th_add_delete_buttons` (point 8)
    * the :ref:`th_lock_button` (point 9)
    
.. _th_search_box:

search box
^^^^^^^^^^

    .. image:: ../../../_images/components/th/search_box.png
    
    In the search box user can select the :ref:`columns <column>` through which
    there will be made a query: a query allow to reduce the records visualized in the
    :ref:`th_gui_central_pane` in order to find the record one want to get.
    
.. _th_query_bar:
    
query operator box
^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/query_operator_box.png
    
    The query operator allow to select the SQL operator through which
    there will be made the query.
    
    In the left box you can specify the "NOT" operator.
    
    In the right box user can choose between:
    
    * ``contains``: look for columns that contains the characters
      typed from user (case insensitive)
    * ``starts with``: look for columns that starts with the characters
      typed from user (case insensitive)
    * ``equal to``: look for columns that match entirely with the characters
      typed from user (case sensitive)
    * ``word start``: look for columns that contains a word that starts with the
      characters typed from user (case insensitive)
    * ``starts with chars``: look for columns that starts with the characters
      typed from user (case sensitive)
    * ``is null``: look for null columns
    * ``is null or empty``: look for null or empty columns
    * ``in``: add???
    * ``regular expression``: add a regexp
    * ``greater than``: look for columns that contains a greater number respect to a number
      typed from user (works for numerical columns)
    * ``greater or equal to``: look for columns that contains a greater or equal number
      respect to a number typed from user (works for numerical columns)
    * ``less than``: look for columns that contains a smaller number respect to a
      number typed from user (works for numerical columns)
    * ``less or equal to``: look for columns that contains a smaller or equal number
      respect to a number typed from user (works for numerical columns)
    * ``between``: look for columns that contains a number contained between two
      numbers typed from user (works for numerical columns). The two numbers must be
      written separated by a comma, like ``value1,value2``
      
.. _th_query_value:

query value box
^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/query_value.png
    
    In the query value user can specify the value for the SQL query
    
.. _th_run_query_button:

run query button
^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/GUI/view_actionbar/run.png
       :align: left
       
    The run query button allows to start the query. To start a query, you can otherwise press "ENTER"
    
.. _th_query_actions:

query action buttons
^^^^^^^^^^^^^^^^^^^^

    You find here some buttons that allow user to perform different actions. You can modify
    the preset of buttons following the instructions of the add??? section
    
    In particular, user finds the following buttons:
    
    .. image:: ../../../_images/components/th/GUI/view_actionbar/lens.png
       :align: left
       :width: 22px
       
    **Query tool**: allow to perform more complex queries and save them
    
    .. image:: ../../../_images/components/th/GUI/view_actionbar/excel.png
       :align: left
       :width: 22px
       
    **Export**: export the result of the query in an excel file
    
    .. image:: ../../../_images/components/th/GUI/view_actionbar/print.png
       :align: left
       :width: 22px
       
    **Print**: print the result of the query
    
    .. image:: ../../../_images/components/th/GUI/view_actionbar/settings.png
       :align: left
       :width: 22px
       
    **Settings**: add??? (not working yet)
    
    .. image:: ../../../_images/components/th/GUI/view_actionbar/mail.png
       :align: left
       :width: 22px
       
    **Mail**: add??? (not working yet)
    
.. _th_query_result_numbers:

query result numbers
^^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/GUI/numbers.png
       :align: left
       :width: 45px
       
    This icon shows the numbers of records that match with the query (the number with the blue
    background) respect to the total number of records (the number with the yellow background)
    
.. _th_add_delete_buttons:

add and delete buttons
^^^^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/GUI/add_delete.png
       :align: left
       :width: 58px
    
    The delete button allow to permanently cancel some records. User must select the records he want
    to cancel before clicking this button. The add button allow to add a new record. The gui for the
    creation of a new record is described in the :ref:`data_entry`
    
    .. note:: to use the delete and the add buttons, user must have the right permits.
              For more information about the permits, check the :ref:`instanceconfig_authentication`
              section of the :ref:`gnr_instanceconfig` page
              
.. _th_lock_button:

lock button
^^^^^^^^^^^

    .. image:: ../../../_images/components/th/GUI/locker.png
       :align: left
       :width: 22px
       
    The lock button allow to unlock the :ref:`th_add_delete_buttons`, in order to delete, modify
    or create new records
    
.. _th_gui_central_pane:

central pane
------------

    The central pane contains all the stuff you define in the :ref:`th_view_class`.
    
    Usual the central pane is used to visualize a :ref:`grid` with the records saved in the
    database:
    
    .. image:: ../../../_images/components/th/GUI/columns_view.png
    
    The columns pane allows user to see all that records that satisfy his SQL query.
    Every record show the columns you have inserted in the :ref:`th_struct` method.
    
    Through the :ref:`th_conf_views` (opened through the button "1" in the figure) user can
    create more than one preset views
    
.. _th_conf_views:

configurable-views bar
^^^^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/GUI/conf_views/conf_views.png
       :align: left
       :width: 217px
       
    The "configurable-views bar" allows the user to create views.
    
    In the image, "id", "Code", "Description", "Full Descr.", "Product Type" and
    "Products Type" are the name of the :ref:`columns` of the :ref:`database table
    <table>`.
    
    In particular, "Products Type" is colored in green because it is a :ref:`table_relation_column`
    
    .
    
    Let's see all the buttons:
    
    .. image:: ../../../_images/components/th/GUI/conf_views/base.png
       :align: left
       :width: 62px
       
    Change from "Base view" to a custom view (the button will change its label
    when you select another view)
    
    .. image:: ../../../_images/components/th/GUI/conf_views/favorite.png
       :align: left
       :width: 22px
       
    **Favorite view**: Select the current view as the favorite view
    
    .. image:: ../../../_images/components/th/GUI/save.png
       :align: left
       :width: 22px
       
    **Save view**: Save a custom view
    
    .. image:: ../../../_images/components/th/GUI/conf_views/delete.png
       :align: left
       :width: 22px
       
    **Delete view**: Delete a custom view (you can't delete the "Base View")
    
.. _th_gui_view_bottom_bar:

bottom bar
----------

    .. image:: ../../../_images/components/th/bottom_bar.png
    
    The bottom bar is used by default to send message to user (like ... add???).
    
    You can customize it ... add???
    
.. _data_entry:

data-entry window
=================

    The ``data-entry window`` is the GUI of the TableHandler's :ref:`th_form_class`.
    
    It allows to:
    
    * modify, add or delete a single records (user must authenticate himself
      with the right permits to perform these actions - check the :ref:`auth` page for
      more information)
      
    Let's see this image:
    
    .. image:: ../../../_images/components/th/gui_form.png
    
    The form window has been divided through some colored box; in particular you can see:
    
    * the :ref:`th_gui_form_top_bar` (*red* box)
    * the :ref:`th_gui_form_action_bar` (*green* box)
    * the :ref:`th_gui_form_box` (*blue* box)
    * the :ref:`th_gui_form_bottom_bar` (*yellow* box)
    
    In the next sub sections we explain in all the details these parts.
    
.. _th_gui_form_top_bar:

top bar
-------

    .. image:: ../../../_images/components/th/gui_view_topbar.png
    
    The top bar contains:
    
    #. the title of the record (you can customize the title. Check here add???
       for more infomation)
    #. the :ref:`workdate`
    
.. _th_gui_form_action_bar:

action bar
----------

    .. image:: ../../../_images/components/th/GUI/form_actionbar/form_actionbar.png
    
    The action bar contains:
    
    .. image:: ../../../_images/components/th/GUI/form_actionbar/dismiss.png
       :align: left
       :width: 22px
       
    **Dismiss button**: return to the view
    
    .. image:: ../../../_images/components/th/GUI/form_actionbar/revert.png
       :align: left
       :width: 22px
       
    **Revert button**: revert the changes after the last save
    
    .. image:: ../../../_images/components/th/GUI/save.png
       :align: left
       :width: 22px
       
    **Save button**: save the record
    
    .. image:: ../../../_images/components/th/GUI/locker.png
       :align: left
       :width: 22px
       
    **Locker**: lock/unlock all the :ref:`th_gui_form_action_bar` buttons
    
    .. image:: ../../../_images/components/th/GUI/add_delete.png
       :align: left
       :width: 58px
       
    **Add/Delete buttons**: add a new record / delete current record
    
    .. image:: ../../../_images/components/th/GUI/form_actionbar/navigation.png
       :align: left
       :width: 106px
       
    **Navigation buttons**: Allow to move from a record to another one
    
    **Semaphore**: it indicates the save status; in particular:
    
        .. image:: ../../../_images/components/th/GUI/form_actionbar/green.png
           :align: left
           :width: 22px
        
        **green light**: the record is saved
        
        .. image:: ../../../_images/components/th/GUI/form_actionbar/yellow.png
           :align: left
           :width: 22px
           
        **yellow light**: the record has unsaved changes
          
        .. image:: ../../../_images/components/th/GUI/form_actionbar/red.png
           :align: left
           :width: 22px
           
        **red light**: some condition for a correct save is not satisfied (for example,
        a :ref:`validation <validations>` is not satisfied); correct the wrong field
        in order to save the record
        
.. _th_gui_form_box:

form pane
---------

    In the form pane you can find all the stuff defined in the :ref:`th_form_class`.
    
    In particular, you can define a :ref:`form` through which user can save its new records
    (or modify the existing ones), joined to some :ref:`webpage_elements_index` or any other
    stuff.
    
    Let's see this image:
    
    .. image:: ../../../_images/components/th/form_box.png
    
    The image is an example of a simple :ref:`form` with a :ref:`tabcontainer` including in
    the first tab a :ref:`formbuilder`
    
.. _th_gui_form_bottom_bar:

bottom bar
----------

    .. image:: ../../../_images/components/th/bottom_bar.png
    
    The bottom bar is used by default to send message to user (like the correct act of a
    record save).
    
    You can customize it ... add???