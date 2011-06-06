.. _genro_viewform:

=====================
view and data windows
=====================

    Usually the GUI management of a form is made by two sections:
    
    * the :ref:`genro_data_entry`
    * the :ref:`genro_view_data`
    
    These two windows can live in a single :ref:`webpages_webpages`, or in two
    :ref:`genro_stackcontainer`\s, or one in a page and one in a :ref:`genro_dialog`,
    and so on.
    
    There is a :ref:`genro_component` that allows to handle the creation and the
    disposition of these two windows: the :ref:`genro_th`.
    
.. _genro_view_data:

view-data window
================

    The ``view-data window`` allow to:
    
    * visualize the records saved by the user.
    * make a query to search into records
    
    .. image:: ../images/th/view.png
    
.. _genro_data_entry:

data-entry window
=================

    The ``data-entry window`` allow to:
    
    * modify, add or delete a single records (user must authenticate himself
      with the right permits to perform these actions - check the add???
      documentation page for more information)
    
    .. image:: ../images/th/form.png
