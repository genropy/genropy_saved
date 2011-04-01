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
    * Typically, it contains the configuration and WSGI script in the :ref:`sites_root`
      (it is used as the executable if you want to use a debugger, like WingIDE_)
    
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
        * :ref:`genro_instances_index` folder - here lies all your instance folder.
          Every instance folder has got:
          
          * a :ref:`instances_custom` folder
          * a :ref:`instances_data` folder
          * an :ref:`instances_instanceconfig` file
          
        * :ref:`genro_packages_index` folder - here lies all your package folder.
          Every package folder has got:
          
          * a :ref:`packages_lib` folder
          * a :ref:`packages_main` file
          * a :ref:`packages_menu` file
          * a :ref:`packages_model` folder
          * a :ref:`packages_webpages` folder
              * :ref:`genro_webpage_resources` folder
              * one or more :ref:`webpages_webpages`\s
                    
        * :ref:`genro_resources_index` folder
        * :ref:`genro_sites_index` folder - here lies all your sites folder.
          Every site folder has got:
          
          * a :ref:`sites_pages` folder
          * a :ref:`sites_root` file
          * a :ref:`sites_siteconfig` file
    