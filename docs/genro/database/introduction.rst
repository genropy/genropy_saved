===============================
Introduction to a Genro Project
===============================

    GenroPy is a Framework for business applications.
    
    The GenroPy applications are divided into several layers, allowing customization (ensuring an easy upgrade even with customization) and reuse of code and resources among various projects.

.. _genro_SIPC:

Genropy Project
===============
    
    A Genropy Project consists of:
    
    **A site**
    
    * It deals with everything related to the configuration of a particular installation
    * It includes Web components and configurations that are necessary for the execution over the Web
    * Typically, it contains the configuration and WSGI script in the :ref:`sites_root` (it is used as the executable if you want to use a debugger, like WingIDE_)
    
    .. _WingIDE: http://www.wingware.com/
    
    Check the :ref:`genro_sites_index` documentation page for further explanations
    
    **An instance**:
    
    * It contains customizations for the particular customer
    * Usually contains parameters for database access
    * It has a :ref:`instances_data` subfolder that you can use to store data in filesystems
    * When working with the Python interpreter or command line tools, usually working at the instance::
        
        #!python
        from gnr.app.gnrapp import GnrApp
        instance = GnrApp('name_of_project')
        
    * add??? the concept of sub instance, used to change the application configuration at runtime (e.g: to access to historical data already eliminated from the main current database instance)
    
    Check the :ref:`genro_instances_index` documentation page for further explanations
    
    **Packages**:
    
    * They are the various modules that make up the application code to Genro, including the main package, which is the application developed.
    * Genro provides additional modules that implement common functions for all the applications (user management, table of Italian municipalities...)
    
    .. note:: the Genro packages are not Python packages (not a set of linked modules, containing a file ``__init__.py``), and Genro packages can't be imported with the statement ``import`` *module* or with ``from`` *module* ``import``
    
    Check the :ref:`genro_packages_index` documentation page for further explanations
    
    **Components and Resources**:
    
    The components and the resources are common tools reusable for more than one project.
    
    Check the :ref:`genro_components_index` and the :ref:`genro_resources_index` documentation pages for further explanations
    