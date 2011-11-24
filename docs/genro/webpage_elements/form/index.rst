.. _form:

====
form
====
    
    *Last page update*: |today|
    
    * :ref:`form_intro`
    * :ref:`form_section_index`

.. _form_intro:

introduction
============

    A form allows the users to enter data that are sent to a server for processing
    
    Let's see an example of a form:
    
    .. image:: ../../_images/form.png
    
    In genro you can easily handle the creation of a form through the :ref:`formbuilder`.
    
    The formbuilder uses:
    
    * :ref:`widgets` - for users interaction
    * :ref:`validations` - allow to check if the user typing is correct
    
    The form will be saved into a :ref:`bag`. Every row is composed by a single
    form field, with the following sintax::
    
        <field_name _loadedValue="::NN">record_value</field_name>
        
    .. _form_section_index:

section index
=============
        
.. toctree::
    :maxdepth: 1
    :numbered:
    
    form_validations