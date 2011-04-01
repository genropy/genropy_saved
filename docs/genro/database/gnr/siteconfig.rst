.. _genro_gnr_siteconfig:

==============
``siteconfig``
==============

    The ``siteconfig`` folder includes a single file: ``default.xml``
    
.. _genro_gnr_siteconfig_default:
    
``default.xml``
===============

    The ``default.xml`` of the ``.gnr/siteconfig`` folder set the default values of your :ref:`sites_siteconfig` files.
    
    You can obviously redefine the values of the ``siteconfig`` file for every project you make, setting the features directly in the :ref:`sites_siteconfig` of the specific project.
    
    Let's see its structure::
    
        <?xml version='1.0' encoding='UTF-8'?>
        <GenRoBag>
            <wsgi _T="NN"></wsgi>
            <connection_timeout _T="NN"></connection_timeout>
            <connection_refresh _T="NN"></connection_refresh>
            <dojo _T="NN" version="11"></dojo>
        </GenRoBag>
        
    We remind the detailed explanations of the various tags on the :ref:`sites_siteconfig` documentation page.