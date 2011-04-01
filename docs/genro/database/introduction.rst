.. _genro_project:

=======
project
=======
    
    The Genro applications (or projects) are divided into several layers, allowing customization
    (ensuring an easy upgrade even with customization) and reuse of code and resources among
    various projects.
    
    A Genropy Project consists of:
    
    **A ``sites`` folder**
    
    * It deals with everything related to the configuration of a particular installation
    * It includes Web components and configurations that are necessary for the execution
      over the Web
    * Typically, it contains the configuration and WSGI script in the :ref:`sites_root` (it is used as
      the executable if you want to use a debugger, like WingIDE_)
    
    .. _WingIDE: http://www.wingware.com/
    
    Check the :ref:`genro_sites_index` documentation page for further explanations
    
    **An ``instances`` folder**:
    
    * It contains customizations for the particular customer
    * Usually contains parameters for database access
    * It has a :ref:`instances_data` subfolder that you can use to store data in filesystems
    * When working with the Python interpreter or command line tools, usually working at the
      instance::
        
        #!python
        from gnr.app.gnrapp import GnrApp
        instance = GnrApp('name_of_project')
        
    Check the :ref:`genro_instances_index` documentation page for further explanations
    
    **A ``packages`` folder**:
    
    * They are the various modules that make up the application code to Genro, including the main
      package, which is the application developed.
    * Genro provides additional modules that implement common functions for all the applications
      (user management, table of Italian municipalities...)
    
    .. note:: the Genro packages are not Python packages (not a set of linked modules, containing
              a file ``__init__.py``), and Genro packages can't be imported with the statement
              ``import`` *module* or with ``from`` *module* ``import``
    
    Check the :ref:`genro_packages_index` documentation page for further explanations
    
    **A ``resources`` folder**:
    
    It contains components and resources, that are common tools reusable for more than one project.
    
    Check the :ref:`genro_components_index` and the :ref:`genro_resources_index` documentation
    pages for further explanations
    
project structure help
======================

    In this section you can find a tree structure that represents a common structure of a Genro project.
    
    * :ref:`genro_project` folder
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
    