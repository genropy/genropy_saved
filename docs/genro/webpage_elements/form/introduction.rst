.. _genro_form_intro:

============
Introduction
============

    A form allows the users to enter data that are sent to a server for processing.
    
    Let's see an example of form:
    
    .. image:: ../../images/form.png
    
    In genro you can easy handle the creation of a form through the :ref:`genro_formbuilder`.
    
    The formbuilder uses:
    
    * :ref:`genro_form_widgets_index`: for users interaction
    * :ref:`genro_validations`: check the correct form of users input
    * :ref:`genro_field`: a widget creator used to view, select or modify data included in
      a database :ref:`genro_table`.
    
    The form will be saved into a :ref:`genro_bag`. Every row is composed by a single
    form field, with the following sintax::
    
        <field_name _loadedValue="::NN">record_value</field_name>
        
    Usually the GUI management of a form is made by two sections:
    
    * the :ref:`genro_data_entry`
    * the :ref:`genro_view_data`
    
    These two windows can live in a single :ref:`webpages_webpages`, or in two
    stacks, or one in a page and one in a dialog, and so on. The
    :ref:`genro_components` that handles the creation and the disposition
    of these two windows is the :ref:`genro_th`.

.. _genro_view_data:

view-data window
================

    The ``view-data window`` allow to:
    
    * visualize the records saved by the user.
    * make a :ref:`genro_query` to search into records
    
    .. image:: ../../images/th/view.png
    
.. _genro_data_entry:

data-entry window
=================

    The ``data-entry window`` allow to:
    
    * modify, add or delete a single records (user must authenticate himself
      with the right permits to perform these actions - check the add???
      documentation page for more information)
    
    .. image:: ../../images/th/form.png
    