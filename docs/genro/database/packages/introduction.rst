.. _genro_packages_introduction:

============
Introduction
============

    * :ref:`packages_map`
    * :ref:`packages_autofill`
    
    .. module:: gnr.app.gnrdeploy
    
    The ``packages`` folder includes the packages for your application.
    
    .. note:: the Genro packages are not Python packages (so they are not a set of linked modules,
              containing a file ``__init__.py``), and Genro packages can't be imported with the
              statement ``import`` *module* or with ``from`` *module* ``import``
    
.. _packages_map:

``packages`` folder content list
================================

    If you follow the steps of the :ref:`genro_project_autocreation` section, inside your
    ``packages`` folder you will find  a ``package`` folder including a ``lib`` folder, a
    ``model`` folder, a ``webpages`` folder, a ``main.py`` file and a ``menu.xml`` file.
    
    You can use the package automatically created as your main package. You can create
    more than one package in your project.
    
    Click on the following links for more information on the content of a single package:
    
    * the :ref:`packages_lib` folder
    * :ref:`packages_main`
    * :ref:`packages_menu`
    * the :ref:`packages_model` folder
    * the :ref:`packages_webpages` folder
    
.. _packages_autofill:

autocreation of the ``packages`` folder
=======================================

    To create a new package folder you can type in your terminal::
    
        gnrmkpackage packagename
        
    where ``packagename`` is the name of your package.
    
    Your ``packages`` folder will look like this one:
    
    .. image:: ../../images/structure/structure-packages.png
    
    In this example we call the package ``myproject``, like the project name. It is a convention
    to call the first package (the main one) with the name of the project.
    
    .. note:: The autocreation of this folder is handled by the :class:`InstanceMaker` class.
