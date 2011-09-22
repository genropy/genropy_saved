.. _project:

=======
project
=======
    
    *Last page update*: |today|
    
    * :ref:`project_intro`
    * :ref:`project_section_index`

.. _project_intro:

introduction
============
    
    In this section we explain how to build a Genro project database management.
    
    The Genro applications (or projects) are divided into several layers, allowing
    customization and reuse of code and resources among various projects.
    
    A Genropy Project is structured in a main ``project`` folder with 4 subfolders,
    called: ``sites``, ``instances``, ``packages`` and ``resources``.
    
    .. image:: ../_images/projects/myproject.png
    
    (*in the image, ``projectName`` is the name of the project*)
    
    Let's introduce the 4 subfolders:
    
    * The ``instances`` folder:
    
        * It contains customizations for the particular customer
        * Usually contains parameters for database access
        * It has a ``data`` subfolder that you can use to store data in filesystems
        * When working with the Python interpreter or command line tools, usually working at the
          instance::
            
            #!python
            from gnr.app.gnrapp import GnrApp
            instance = GnrApp('name_of_project')
          
        More information in the :ref:`instances_index` section.
        
    * The ``packages`` folder:
    
        * It contains the various modules that make up the application code to Genro [#]_.
          
          .. note:: the Genro packages are not Python packages (not a set of linked modules,
                    containing a file ``__init__.py``), and Genro packages can't be imported
                    with the statement ``import`` *module* or with ``from`` *module* ``import``
                    
        More information in the :ref:`packages_index` section.
        
    * The ``resources`` folder:
    
        * It is a place for a lot of useful tool, like components (python modules), CSS files,
          js scripts, and so on.
          
        * You will use it for all the common tools of your project.
        
        For an introduction to the resources, please check the :ref:`intro_resources` page.
        
    * The ``sites`` folder:
    
        * It deals with everything related to the configuration of a particular installation
        * It includes Web components and configurations that are necessary for the execution
          over the Web
        * Typically, it contains the configuration and WSGI script (it is used as the executable
          if you want to use a debugger, like WingIDE_)
          
          .. _WingIDE: http://www.wingware.com/
          
        More information in the :ref:`sites_index` section
        
.. _project_section_index:

section_index
=============
    
.. toctree::
    :maxdepth: 2
    
    project_structures
    introduction to the resources <intro_resources>
    the ``.gnr`` folder <gnr/index>
    the ``instances`` folder <instances/index>
    the ``packages`` folder <packages/index>
    the ``resources`` folder <resources/index>
    the ``sites`` folder <sites/index>
    tutorial/index
    
**Footnotes**:

.. [#] Genro provides additional modules that implement common functions for all the applications (user management, table of Italian municipalities...)
