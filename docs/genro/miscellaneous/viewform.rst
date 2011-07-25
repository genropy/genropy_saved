.. _genro_viewform:

=====================
view and form windows
=====================
    
    *Last page update*: |today|
    
    * :ref:`view_form_intro`
    * :ref:`genro_view_data`
    * :ref:`genro_data_entry`
    
.. _view_form_intro:

introduction
============
    
    The GUI of a database :ref:`genro_project` is usually composed by two sections:
    
    * the :ref:`genro_view_data`
    * the :ref:`genro_data_entry`
    
    These two windows can live in a single :ref:`webpages_webpages`, or in two
    :ref:`stackContainers <genro_stackcontainer>`, or one in a page and one in a
    dialog, and so on.
    
    In Genro you find a pre-set GUI for the management of ``view-data window`` and
    the ``data-entry window``: the :ref:`genro_th` component.
    
.. _genro_view_data:

view-data window
================

    The ``view-data window`` should allow to:
    
    * visualize the records saved by the user
    * make a query to search into records
    
    .. image:: ../_images/components/th/view.png
    
    If you use the :ref:`genro_th` component you have a pre-set GUI that carries those features.
    
.. _genro_data_entry:

data-entry window
=================

    The ``data-entry window`` allow to:
    
    * modify, add or delete a single records (user must authenticate himself
      with the right permits to perform these actions - check the add???
      documentation page for more information)
    
    .. image:: ../_images/components/th/form.png
    
    If you use the :ref:`genro_th` component you have a pre-set GUI that carries those features.