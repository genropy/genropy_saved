.. _genro_sites_introduction:

============
Introduction
============
    
    .. image:: ../../images/projects/sites/project_sites.png
    
    * :ref:`sites_map`
    * :ref:`sites_autofill`
    
    .. module:: gnr.app.gnrdeploy
    
    The ``sites`` folder:
    
    * deals with everything related to the configuration of a particular installation
    * includes Web components and configurations that are necessary for the execution over
      the Web
    * typically contains the configuration and WSGI script in the :ref:`sites_root` (it is
      used as the executable if you want to use a debugger, like WingIDE_)
    
    .. _WingIDE: http://www.wingware.com/
    
.. _sites_map:

``sites`` folder content list
=============================

    If you follow the steps of the :ref:`genro_project_autocreation` section, inside your
    ``sites`` folder you will find a ``site`` folder including ``pages`` folder, a ``root``
    file and a ``siteconfig`` file.
    
    Click on the following links for informations about them:
    
    * :ref:`sites_pages`
    * :ref:`sites_root`
    * :ref:`sites_siteconfig`
        
.. _sites_autofill:

autocreation of the ``sites`` folder
====================================

    You can create a ``sites`` folder typing::
    
        gnrmksite sitesName
        
    where ``sitesName`` is the name of your ``sites`` folder (that we suggest you to call as your
    :ref:`genro_project` folder).
    
    Your ``sites`` folder will look like this one:
    
    .. image:: ../../images/projects/sites/sites.png
    