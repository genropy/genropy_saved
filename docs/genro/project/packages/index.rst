.. _packages:

============
``packages``
============
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/packages/project_packages.png
    
    * :ref:`packages_intro`
    * :ref:`packages_section_index`
    
.. _packages_intro:
    
introduction
============

    The ``packages`` folder includes the packages for your application.
    
    A package is composed principally by some database :ref:`tables <table>` and by some
    :ref:`webpages <webpage>`
    
    .. note:: The Genro packages are not Python packages (so they are not a set of
              linked modules, containing a file ``__init__.py``), and Genro packages
              can't be imported with the statement ``import`` *module* or with ``from``
              *module* ``import``
              
.. _packages_section_index:

section index
=============

.. toctree::
    :maxdepth: 2
    
    basic_structure
    lib
    main
    menu
    model/index
    resources/index
    webpages/index