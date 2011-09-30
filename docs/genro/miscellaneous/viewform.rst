.. _viewform:

=====================
view and form windows
=====================
    
    *Last page update*: |today|
    
    * :ref:`view_form_intro`
    * :ref:`view_data`
    * :ref:`data_entry`
    
.. _view_form_intro:

introduction
============
    
    The GUI of a database :ref:`project` is usually composed by two sections:
    
    * the :ref:`view_data`
    * the :ref:`data_entry`
    
    These two windows can live in a single :ref:`webpage`, or in two
    :ref:`stackContainers <stackcontainer>`, or one in a page and one in a
    dialog, and so on.
    
    In Genro you find a pre-set GUI for the management of ``view-data window`` and
    the ``data-entry window``: the :ref:`th` component.
    
.. _view_data:

view-data window
================

    The ``view-data window`` should allow to:
    
    * visualize the records saved by the user
    * make a query to search into records
    
    .. image:: ../_images/components/th/view.png
    
    If you use the :ref:`th` component you have a pre-set GUI that carries those features.
    
.. _data_entry:

data-entry window
=================

    The ``data-entry window`` allow to:
    
    * modify, add or delete a single records (user must authenticate himself
      with the right permits to perform these actions - check the :ref:`auth` page for
      more information)
    
    .. image:: ../_images/components/th/form.png
    
    If you use the :ref:`th` component you have a pre-set GUI that carries those features.