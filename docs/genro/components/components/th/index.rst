.. _th:

============
TableHandler
============

    *Last page update*: |today|
    
    .. note:: summary of the component requirements:
              
              * It is a :ref:`components_standard`.
              * It can be used both as an :ref:`components_active` or as a :ref:`components_passive`:
              
                * :ref:`webpages_py_requires` to use the component as an **active component**::
                  
                      py_requires = 'public:TableHandlerMain'
                      
                * :ref:`webpages_py_requires` to use the component as a **passive component**::
                      
                      py_requires = 'th/th:TableHandler'
    
    * :ref:`th_intro`
    * :ref:`th_section_index`
    
.. _th_intro:

introduction
============

    1. The TableHandler is the Genro way to handle data visualization and data entry
    
    2. The TableHandler is structured in two main classes:
       
       * the :ref:`th_view_class` to manage data visualization
       * the :ref:`th_form_class` to manage data entry
       
       These two classes will be visualized respectively into a :ref:`view_data`:
       
       .. image:: ../../../_images/components/th/view.png
       
       and into a :ref:`data_entry`:
       
       .. image:: ../../../_images/components/th/form.png
       
    3. The TableHandler carries many features:
       
       * The TableHandler automatically handles the management of data recording
       * The TableHandler is fully customizable:
       
         * manipulating the main structure of View and Form classes: more information
           in the :ref:`th_map` page
         * choosing the CSS icons set: more information in the :ref:`css_icons` section
         * choosing the GUI of your *data-entry window* from a set of options
           (e.g: dialog, palette, stackcontainer...): more information in the
           :ref:`th_types` page
           
    4. You can build the TableHandler:
       
       * inside a :ref:`webpage`
       * externally as a :ref:`th_resource_page`
       
       add???
       
       You can create your TableHandlers into the :ref:`intro_resources` folder
       of your :ref:`projects <project>` - in this case we talk about
       :ref:`th_resource_page`: this form allow to reuse the TableHandlers you
       have created in more than a webpage (and in more than a package)
       
.. _th_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    
    th_paths
    th_pages
    th_components
    th_further_info
    th_gui