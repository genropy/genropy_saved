.. _project_structure:

=================
project structure
=================
    
    *Last page update*: |today|
    
    * :ref:`project_basic_structure`
    * :ref:`project_autocreation` (:ref:`project_help`)
    
.. _project_basic_structure:

basic structure
===============

    In this section you can find the basic structure of a Genro project. Click on the
    relative links for more information on every single file/folder, including the 4
    main project subfolders:
    
    * ``project`` folder
        * :ref:`instances_index` folder - here lies all your instance folder.
          Every instance folder has got:
          
          * a :ref:`instances_custom` folder
          * a :ref:`instances_data` folder
          * an :ref:`instances_instanceconfig` file
          
        * :ref:`packages_index` folder - here lies all your package folder.
          Every package folder has got:
          
          * a :ref:`packages_lib` folder
          * a :ref:`packages_main` file
          * a :ref:`packages_menu` file
          * a :ref:`packages_model` folder
          * a :ref:`public_resources` folder
          * a :ref:`packages_webpages` folder
              * one or more :ref:`webpages <webpages_webpages>`
                    
        * :ref:`private_resources` folder (for all your project :ref:`private resources <private_resource>`)
        * :ref:`sites_index` folder - here lies all your sites folder.
          Every site folder has got:
          
          * a :ref:`sites_pages` folder
          * a :ref:`sites_root` file
          * a :ref:`sites_siteconfig` file
          
.. _project_autocreation:

project autocreation
====================
    
    You can build a project with its four main subfolders with the command line::
    
        gnrmkproject projectName -a
        
    where ``projectName`` is the name you want for your project.
    
    If you write the command line, you will create a project with the following
    structure:
    
    .. image:: ../_images/projects/myproject2.png
    
    .. note:: the name of the istance folder (inside the ``instances`` folder) and the name
              of the site folder (inside the ``sites`` folder) are equal to the name of the
              ``project`` folder. This is a convention to keep order in your project.
              
.. _project_help:

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
       