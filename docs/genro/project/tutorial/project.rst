.. _tt_project:

===============================
creation of a project structure
===============================

    *Last page update*: |today|
    
    To create a project you have to launch the :ref:`gnrmkproject` script (GeNRo MaKe PROJECT)::
        
        gnrmkproject projectName
        
    where ``projectName`` is the name you choose for your project
    
    This will create a folder with the project name you have chosen, and 4 empties subfolders
    called: ``instances``, ``packages``, ``resources``, ``sites``
    
    .. image:: ../../_images/projects/myproject.png
    
    .. note:: the Genro Team prefers to call their projects using only lowercase letters
    
    However, if you want to create a project with both site and instance default features
    (that we will explain later in the following sections), you have to write::
    
        gnrmkproject projectname -a
        
    You can see the result in this image:
    
    TODO image...
    
    Now type the command line ``gnrmkproject projectname -a`` and check the tree structure you
    have created (the 4 subfolders and the contents of the ``instances`` and ``sites`` folders).
    In the next sections we'll begin to explain all the details of the project's subfolders