.. _genro_form_intro:

============
Introduction
============
    
    *Last page update*: |today|
    
    A form allows the users to enter data that are sent to a server for processing.
    
    Let's see an example of form:
    
    .. image:: ../../_images/form.png
    
    In genro you can easy handle the creation of a form through the :ref:`genro_formbuilder`.
    
    The formbuilder uses:
    
    * :ref:`genro_form_widgets_index`: for users interaction
    * :ref:`genro_validations`: check the correct form of users input
    * :ref:`genro_field`: a widget creator used to view, select or modify data included in
      a database :ref:`genro_table`.
    
    The form will be saved into a :ref:`genro_bag`. Every row is composed by a single
    form field, with the following sintax::
    
        <field_name _loadedValue="::NN">record_value</field_name>