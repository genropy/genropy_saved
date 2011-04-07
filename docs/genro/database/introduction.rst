.. _genro_project:

=======
project
=======
    
    * :ref:`genro_project_introduction`
    * :ref:`genro_project_basic_structure`
    * :ref:`genro_project_autocreation`
    
.. _genro_project_introduction:

Introduction
============
    
    The Genro applications (or projects) are divided into several layers, allowing
    customization (ensuring an easy upgrade even with customization) and reuse of
    code and resources among various projects.
    
    A Genropy Project is structured in a main ``project`` folder with 4 subfolders,
    called: ``sites``, ``instances``, ``packages`` and ``resources``:
    
    * The ``sites`` folder:
    
        * It deals with everything related to the configuration of a particular installation
        * It includes Web components and configurations that are necessary for the execution
          over the Web
        * Typically, it contains the configuration and WSGI script (it is used as the executable
          if you want to use a debugger, like WingIDE_)
        
        .. _WingIDE: http://www.wingware.com/
        
    * The ``instances`` folder:
    
        * It contains customizations for the particular customer
        * Usually contains parameters for database access
        * It has a ``data`` subfolder that you can use to store data in filesystems
        * When working with the Python interpreter or command line tools, usually working at the
          instance::
            
            #!python
            from gnr.app.gnrapp import GnrApp
            instance = GnrApp('name_of_project')
            
    * The ``packages`` folder:
    
        * It contains the various modules that make up the application code to Genro [#]_
        
        .. note:: the Genro packages are not Python packages (not a set of linked modules, containing
                  a file ``__init__.py``), and Genro packages can't be imported with the statement
                  ``import`` *module* or with ``from`` *module* ``import``
        
    * The ``resources`` folder:
    
        It contains every useful tool, like components (python modules), CSS, js scripts, and so on.
        
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
    
    You can build a project with its four main subfolders with the command line [#]_::
    
        gnrmkproject projectname -a
        
    where ``projectname`` is the name you want for your project.
    
    If you create a project called "myproject", you will obtain this structure:
    
    .. image:: ../images/myproject2.png
    
    If you're new on the idea of a project, we suggest you, before continuing on this chapter,
    to check the tutorial on the :ref:`genro_simpleproject_index`
    
**Footnotes**:

.. [#] Genro provides additional modules that implement common functions for all the applications
       (user management, table of Italian municipalities...)
.. [#] For a complete reference of the project building options, please check the
       :ref:`genro_project_help` section
    