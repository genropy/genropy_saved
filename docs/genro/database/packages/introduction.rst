.. _genro_packages_introduction:

============
introduction
============

    .. image:: ../../images/projects/packages/project_packages.png
    
    * :ref:`packages_autofill`
    
    .. module:: gnr.app.gnrdeploy
    
    The ``packages`` folder includes the packages for your application. A package
    is composed principally by some database :ref:`genro_table`\s and by some
    :ref:`webpages_webpages`\s.
    
    .. note:: The Genro packages are not Python packages (so they are not a set of
              linked modules, containing a file ``__init__.py``), and Genro packages
              can't be imported with the statement ``import`` *module* or with ``from``
              *module* ``import``.
    
    Every Genro package has got a corresponding sql schema. We suggest you to call both the
    package and the schema with the **same name** - this simplifies your work. Otherwise,
    if you keep different names for the package and for the schema, remember that when you
    make an sql query - on any other sql operation - you have to refer the query to the schema
    name, while when you operate on the package, you have to call it with the package name).
    
.. _packages_autofill:

autocreation of a package
=========================

    If you follow the steps of the :ref:`genro_project_autocreation` section, inside your
    project you have the 4 subfolders we spoke in the
    :ref:`project introduction <genro_project_introduction>` in which a project is commonly
    structured.
    
    To create a project inside the ``packages`` subfolder, you can type in your terminal::
    
        gnrmkpackage packageName
        
    where ``packageName`` is the name you want to give to your package.
    
    When you do this, inside your ``packages`` folder you will find:
    
    * a :ref:`packages_lib` folder
    * a :ref:`packages_main` file
    * a :ref:`packages_menu` file
    * a :ref:`packages_model` folder
    * a :ref:`public_resources` folder (for :ref:`genro_public_resource`\s)
    * a :ref:`packages_webpages` folder
    
    In the following image you see the structure of a project called ``my_project`` with
    a package called ``base``:
    
    .. image:: ../../images/projects/packages/autocreation_packages.png
    
    You can create more than one package in your project, repeating the instructions
    of this section.
    