.. _genro_simple_introduction:

============
introduction
============

    *Last page update*: |today|
    
    .. warning:: chapter to be rewritten completely! --> guide through the "invoice" tutorial?
    
    * :ref:`genro_project_creation`
    
.. _genro_project_creation:

create a Genro project
======================

    We want now help you on a creation of a simple project for a management of a database.
    
    To create a project you have to type in your command window the following line (but please don't do it for now!) [#]_::
        
        gnrmkproject projectname
        
    This will create a folder with the project name you have chosen, and 4 empties subfolders called: ``instances``, ``packages``, ``genro_resources``, ``genro_sites``.
    
    In the following image you can see the project folder with its relative subfolders (we choose ``myproject`` as project name):
    
    add??? image...
    
    .. note:: the Genro Team prefers to call their projects using only lowercase letters.
    
    However, if you want to create a project with both site and instance default features (that we will explain later in the following sections), you have to write::
    
        gnrmkproject projectname -a
        
    You can see the result in this image:
    
    add??? image...
    
    Now type the command line ``gnrmkproject projectname -a`` and check the tree structure you have created (the 4 subfolders and the contents of the ``instances`` and ``sites`` folders). In the next sections we'll begin to explain all the details of the project's subfolders.
    
**Footnotes**:

.. [#] ``gnrmkproject`` abbrevation has the meaning of ``GeNRo MaKe PROJECT``.
