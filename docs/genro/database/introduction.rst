.. _genro_project:

=======
project
=======
    
    * :ref:`genro_project_introduction`
    * :ref:`genro_project_basic_structure`
    * :ref:`genro_project_autocreation`, :ref:`genro_project_help`
    
.. _genro_project_introduction:

Introduction
============
    
    The Genro applications (or projects) are divided into several layers, allowing
    customization and reuse of code and resources among various projects.
    
    A Genropy Project is structured in a main ``project`` folder with 4 subfolders,
    called: ``sites``, ``instances``, ``packages`` and ``resources``.
    
    * The ``sites`` folder:
    
        * It deals with everything related to the configuration of a particular installation
        * It includes Web components and configurations that are necessary for the execution
          over the Web
        * Typically, it contains the configuration and WSGI script (it is used as the executable
          if you want to use a debugger, like WingIDE_)
          
          .. _WingIDE: http://www.wingware.com/
          
        More information in the :ref:`genro_sites_index` documentation section.
        
    * The ``instances`` folder:
    
        * It contains customizations for the particular customer
        * Usually contains parameters for database access
        * It has a ``data`` subfolder that you can use to store data in filesystems
        * When working with the Python interpreter or command line tools, usually working at the
          instance::
            
            #!python
            from gnr.app.gnrapp import GnrApp
            instance = GnrApp('name_of_project')
          
        More information in the :ref:`genro_instances_index` documentation section.
        
    * The ``packages`` folder:
    
        * It contains the various modules that make up the application code to Genro [#]_.
          
          .. note:: the Genro packages are not Python packages (not a set of linked modules,
                    containing a file ``__init__.py``), and Genro packages can't be imported
                    with the statement ``import`` *module* or with ``from`` *module* ``import``
                    
        More information in the :ref:`genro_packages_index` documentation section.
        
    * The ``resources`` folder:
    
        * It is a place for a lot of useful tool, like components (python modules), CSS files,
          js scripts, and so on.
          
        * You will use it for all the common tools of your project.
        
        More information in the :ref:`genro_resources_index` documentation section.
        
.. _genro_project_basic_structure:

Basic structure
===============

    In this section you can find the basic structure of a Genro project. Click on the
    relative links for more information on every single file/folder, including the 4 subfolders
    we were talking about:
    
    * ``project`` folder
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
                    
        * :ref:`genro_resources_index` folder (for all your project resources)
        * :ref:`genro_sites_index` folder - here lies all your sites folder.
          Every site folder has got:
          
          * a :ref:`sites_pages` folder
          * a :ref:`sites_root` file
          * a :ref:`sites_siteconfig` file
          
.. _genro_project_autocreation:

Project autocreation
====================
    
    You can build a project with its four main subfolders with the command line ::
    
        gnrmkproject projectname -a
        
    where ``projectname`` is the name you want for your project.
    
    If you create a project called "myproject", you will obtain this structure:
    
    .. image:: ../images/myproject2.png
    
.. _genro_project_help:

terminal help
-------------

    You can create a project setting many options. Type::
    
        gnrmkproject -h
        
    to call an help that explains all the possibilities::
    
        Usage: gnrmkproject [options]
        
        Options:
          -h, --help            show this help message and exit
          -b BASE_PATH, --base-path=BASE_PATH
                                base path where project will be created
          -s, --create-site     create site
          -i, --create-instance
                                create instance
          -a, --create-all      create both site and instance
          -p WSGI_PORT, --wsgi-port=WSGI_PORT
                                Specify WSGI port
          -r WSGI_RELOAD, --wsgi-reload=WSGI_RELOAD
                                Specify WSGI autoreload
          -d WSGI_DEBUG, --wsgi-debug=WSGI_DEBUG
                                Specify WSGI debug
                                
**Footnotes**:

.. [#] Genro provides additional modules that implement common functions for all the
       applications (user management, table of Italian municipalities...)
.. [#] For a complete reference of the project building options, please check the
       :ref:`genro_project_help` section
    