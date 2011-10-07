.. _th_gui:

================
Tablehandler GUI
================

    *Last page update*: |today|
    
    * :ref:`th_gui_intro`
    * :ref:`th_gui_view`
    * :ref:`th_gui_form`
    
.. _th_gui_intro:

TableHandler GUI - introduction
===============================

    In the following sections we discover the TableHandler's GUI.
    
    Let's see this image:

    .. image:: ../../../_images/components/th/gui.png
    
    * The Tablehandler view class and form class take place into the central pane (point 2)
    * Points 1, 3 and 4 belong to the :ref:`frameindex` component
    
    The combination of a TableHandler in a :ref:`project` with the frameindex component is a good
    solution for having a quick pre-defined gui.
    
    However, in this page we'll talk about the view class and form class GUI, that is, the central
    pane (point 2). For more information on points 1, 3 and 4, please check the :ref:`frameindex` page.
    
.. _th_gui_view:
    
TableHandler GUI - view class page
==================================

    In this section we describe all the pre-set tools built by the TableHandler's
    :ref:`th_view_class`. In the next section we'll explain the gui of the :ref:`th_form_class`
    
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

    .. image:: ../../../_images/components/th/gui_view_actionbar.png
    
    The action bar allow to perform many actions. In particular you can find:
    
    * the :ref:`th_grid_options` (point 1)
    * the :ref:`th_search_box` (point 2)
    * the :ref:`th_query_bar` (points 3 and 3b)
    * the :ref:`th_query_value` (point 4)
    * the :ref:`th_run_query_button` (point 5)
    * the :ref:`th_query_actions` (point 6)
    * the :ref:`th_query_result_numbers` (point 7)
    * the :ref:`th_add_delete_buttons` (point 8)
    * the :ref:`th_lock_button` (point 9)
    
.. _th_grid_options:

grid options button
^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/grid_options.png
    
    Here you find some options that allow to modify the columns you see in the view.
    
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
    
    In the query value user can specify the value for the SQL query.
    
.. _th_run_query_button:

run query button
^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/run_query_button.png
    
    The run query button allows to start the query. To start a query, you can otherwise
    press "ENTER".
    
.. _th_query_actions:

query action buttons
^^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/query_action_buttons.png
    
    You find here some buttons that allow user to perform different actions. You can modify
    the preset of buttons: follow the instructions of the add??? section!
    
    In particular user finds the following buttons:
    
    * query tool: allow to perform more complex queries (user can add more than one parameter
      for his query) and save them. The parameters through which user can choose are
      the same of the :ref:`th_query_bar`
    * stored query (1): it contains the saved query
    * stored query (2): it contains the different preset views
    * export: export the result of the query in an excel file
    * print: print the result of the query
    * settings: add???
    * mail: allow to send an email
    
.. _th_query_result_numbers:

query result numbers
^^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/query_result_numbers.png
    
    Here you can find the numbers of records that match with the query (the number with the blue
    background) respect to the total number of records (the number with the yellow background)
    
.. _th_add_delete_buttons:

add and delete buttons
^^^^^^^^^^^^^^^^^^^^^^

    .. image:: ../../../_images/components/th/add_delete_buttons.png
    
    The delete button allow to permanently cancel some records. User must select the records he want
    to cancel before clicking this button.
    
    The add button allow to add a new record. The gui for the creation of a new record is described
    in the :ref:`th_gui_form`.
    
    .. note:: to use the delete and the add buttons, user must have the right permits.
              For more information about the permits, check the :ref:`instanceconfig_authentication`
              section of the :ref:`gnr_instanceconfig` page
              
.. _th_lock_button:

lock button
^^^^^^^^^^^

    .. image:: ../../../_images/components/th/lock_buttons.png
    
    The lock button allow to unlock the :ref:`th_add_delete_buttons`, in order to delete or modify
    records or create new ones.
              
.. _th_gui_central_pane:

central pane
------------

    The central pane contains all the stuff you define in the :ref:`th_view_class`.
    
    In particular, you can use the central pane as "columns view"
    
    **central pane - columns view**:
    
    .. image:: ../../../_images/components/th/columns_view.png
    
    The columns pane allows user to see all that records that satisfy his SQL query.
    Every record doesn't show necessary all of its columns, but only the ones you have
    inserted in the :ref:`th_struct` method.
    
    You can create more than one pre-set of view, that is a set of different showed columns,
    through the add??? method.
    
    User can choose the preferred one through the stored query (one of the
    :ref:`th_query_actions`)
    
.. _th_gui_view_bottom_bar:

bottom bar
----------

    .. image:: ../../../_images/components/th/bottom_bar.png
    
    The bottom bar is used by default to send message to user (like ... add???).
    
    You can customize it ... add???
    
.. _th_gui_form:

TableHandler GUI - form class page
==================================

    In this section we describe all the pre-set tools built by the
    TableHandler's :ref:`th_form_class`.
    
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
    
    #. the title of the record (you can customize the title. Check :ref:`here <add???>`
       for more infomation)
    #. the :ref:`workdate`
    
.. _th_gui_form_action_bar:

action bar
----------

    .. image:: ../../../_images/components/th/form_action_bar.png
    
    The action bar contains:
    
    * the navigation buttons (point 1), that are in order from left to right: "first", "previous",
      "next", "last"); they allow to move from a record to another one
    * the semaphore (point 2): it indicates the save status; in particular:
    
        * green light: the record is saved
        * yellow light: the record has unsaved changes (click on the "save" button when
          you want to save them)
        * red light: some condition for a correct save is not satisfied (for example,
          a :ref:`validation <validations>` is not satisfied); correct the wrong field
          in order to save the record
          
    * the management buttons (point 3), that are in order from left to the right:
        
        * "delete current record": delete the current record
        * "add a new record": add a new record
        * "revert": revert the last changes, that are the changes after the last save
        * "save": save the record
        
    * the dismiss button (point 4): it allows to return to the view. If you didn't save your
      record, you will lose the unsaved changes (or the same record, if it is new)
    * the lock button (point 5): it allows to unlock the buttons of the points 1 and 3
    
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
    the first tab a :ref:`formbuilder`.
    
.. _th_gui_form_bottom_bar:

bottom bar
----------

    .. image:: ../../../_images/components/th/bottom_bar.png
    
    The bottom bar is used by default to send message to user (like the correct act of a
    record save).
    
    You can customize it ... add???