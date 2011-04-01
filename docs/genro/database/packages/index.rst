.. _genro_packages_index:

============
``packages``
============

    * :ref:`packages_autofill`
    * :ref:`packages_map`
    
    .. module:: gnr.app.gnrdeploy
    
    The ``packages`` folder includes the packages for your application.
    
    .. note:: the Genro packages are not Python packages (not a set of linked modules, containing a file ``__init__.py``), and Genro packages can't be imported with the statement ``import`` *module* or with ``from`` *module* ``import``
    
.. _packages_autofill:
    
autocreation of the ``packages`` folder
=======================================

    You can create a ``packages`` folder typing::
    
        gnrmkpackage packagename
        
    where ``packagename`` is the name of your package (we suggest you to call your package with the name you gave to your :ref:`genro_structure_mainproject`).
    
    Your ``packages`` folder will look like this one:
    
    .. image:: ../../../images/structure/structure-packages.png
    
    where ``myproject`` is the name of your package.
    
    .. note:: The autocreation of this folder is handled by the :class:`InstanceMaker` class.
    
.. _packages_map:
    
``packages`` folder content list
================================
    
    If you follow the steps of the previous section, inside your ``packages`` folder you will find a ``package`` folder including a ``lib`` folder, a ``model`` folder, a ``webpages`` folder, a ``main.py`` file and a ``menu.xml`` file.
    
    Click on the following links for more information on them:

.. toctree::
    :maxdepth: 1
    
    package_name
    lib
    main
    menu
    model/index
    webpages/index