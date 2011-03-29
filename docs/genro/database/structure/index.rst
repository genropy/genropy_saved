.. _genro_structure_projectstructure:

======================
project structure help
======================

    In this section you can find a tree structure that represents a Genro project common structure: if you need some help with a single file or folder, this is the right place for you.
    
    * :ref:`genro_structure_mainproject` folder
        * :ref:`genro_instances_index` folder - include all your instances folder
            * :ref:`instances_instance_name` folder (*instance_name* is the name of one of your instance folder)
                * :ref:`instances_custom` folder
                * :ref:`instances_data` folder
                * :ref:`instances_instanceconfig`
        * :ref:`genro_packages_index` folder
            * :ref:`packages_package_name` folder (*package_name* is the name of one of your package folder)
                * :ref:`packages_lib` folder
                * :ref:`packages_main`
                * :ref:`packages_menu`
                * :ref:`packages_model` folder
                * :ref:`packages_webpages` folder
                    * :ref:`genro_webpage_resources` folder
                    * one or more :ref:`webpages_webpages`\s
        * :ref:`genro_resources_index` folder
        * :ref:`genro_sites_index` folder
            * :ref:`sites_sites_name` folder - (*sites_name* is the name of one of your site folder)
                * :ref:`sites_pages`
                * :ref:`sites_root`
                * :ref:`sites_siteconfig`
                
index of project structure help
===============================

.. toctree::
    :maxdepth: 2
    
    mainproject
    instances/index
    packages/index
    resources/index
    sites/index