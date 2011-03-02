.. _genro_sites_index:

=====
sites
=====
    
    * :ref:`sites_features`
    * :ref:`sites_autofill`
    * :ref:`sites_map`
    
    .. module:: gnr.app.gnrdeploy
    
.. _sites_features:

features
========
    
    The ``sites`` folder:
    
    * deals with everything related to the configuration of a particular installation
    * includes Web components and configurations that are necessary for the execution over the Web
    * Typically contains the configuration and WSGI script in the :ref:`sites_root` (it is used as the executable if you want to use a debugger, like WingIDE_)
    
    .. _WingIDE: http://www.wingware.com/
    
.. _sites_autofill:

autocreation of the ``sites`` folder
====================================

    You can create a ``sites`` folder typing::
    
        gnrmksite sitesname
        
    where ``sitesname`` is the name of your ``sites`` folder (that we suggest you to call as your :ref:`genro_structure_mainproject` folder).
    
    Your ``sites`` folder will look like this one:
    
    .. image:: ../../../images/structure/structure-sites.png
    
    .. note:: The autocreation of this folder is handled by the :class:`SiteMaker` class.
    
.. _sites_map:

``sites`` folder content list
=============================

    If you follow the steps of the previous section, inside your ``sites`` folder you will find a ``site`` folder including ``pages`` folder, a ``root`` file and a ``siteconfig`` file.
    
    Click on the following links for informations about them:
    
.. toctree::
    :maxdepth: 1
    
    sites_name
    pages
    root
    siteconfig
    