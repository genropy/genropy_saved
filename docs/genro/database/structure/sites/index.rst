.. _genro_sites_index:

=====
sites
=====

    * :ref:`sites_autofill`
    * :ref:`sites_map`
    
    .. module:: gnr.app.gnrdeploy
    
    The ``sites`` folder is... add???
    
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
    