.. _sites_basic_structure:

===============
basic structure
===============

    *Last page update*: |today|
    
    .. image:: ../../_images/projects/sites/project_sites.png
    
    * :ref:`sites_map`
    * :ref:`sites_autofill`
    
.. _sites_map:

``sites`` folder content list
=============================

    If you follow the steps of the :ref:`project_autocreation` section, inside your
    ``sites`` folder you will find a ``site`` folder including a :ref:`sites_pages`
    folder, a :ref:`sites_root` file and a :ref:`sites_siteconfig` file.
    
    During the execution of the :ref:`gnrwsgisite` script there will be created the :ref:`data_folder`
    folder and the :ref:`automap` file
    
.. _sites_autofill:

autocreation of the ``sites`` folder
====================================

    You can create a ``sites`` folder typing::
    
        gnrmksite sitesName
        
    where ``sitesName`` is the name of your ``sites`` folder (that we suggest you to call
    as your :ref:`project` folder).
    
    Your ``sites`` folder will look like this one:
    
    .. image:: ../../_images/projects/sites/sites.png
    