.. _tutorial_index:

===============================
Tutorial: creation of a project
===============================

    .. warning:: chapter to be rewritten completely! --> guide through the "invoice" tutorial?
    
    *Last page update*: |today|
    
    * :ref:`tutorial_intro`
    * :ref:`tutorial_section_index`
    
.. _tutorial_intro:

introduction
============

    We want now help you on a creation of a simple project for database management
    
    To create a project you have to launch the ``gnrmkproject`` script (GeNRo MaKe PROJECT)::
        
        gnrmkproject projectname
        
    This will create a folder with the project name you have chosen, and 4 empties subfolders called:
    ``instances``, ``packages``, ``resources``, ``sites``
    
    In the following image you can see the project folder with its relative subfolders (we choose
    ``myproject`` as project name):
    
    add??? image...
    
    .. note:: the Genro Team prefers to call their projects using only lowercase letters
    
    However, if you want to create a project with both site and instance default features
    (that we will explain later in the following sections), you have to write::
    
        gnrmkproject projectname -a
        
    You can see the result in this image:
    
    add??? image...
    
    Now type the command line ``gnrmkproject projectname -a`` and check the tree structure you
    have created (the 4 subfolders and the contents of the ``instances`` and ``sites`` folders).
    In the next sections we'll begin to explain all the details of the project's subfolders.
    
.. _tutorial_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    
    firststeps
    showcase/index
    