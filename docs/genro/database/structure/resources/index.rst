.. _genro_resources_index:

=============
``resources``
=============

    The resources are called on :ref:`webpages_webpages` through :ref:`webpages_py_requires`, :ref:`webpages_js_requires` and :ref:`webpages_css_requires`. The :mod:`gnr.web.gnrwsgisite` module manages the mixin resources.
    
    In the ``resources`` folder you can put every *public* resource (follow the relative links for more information about them):
    
    * javascript files
    * :ref:`genro_css`
    * :ref:`genro_components_index`
    
    For *public* we mean that you can use these resources both in your project and in other projects.
    
    .. image:: ../../../images/structure/structure-resources.png
    
    If you want to keep *private* your resources, you have to put your resources in the ``_resources`` folder. For
    more information, check the :ref:`genro_webpage_resources` documentation page.
    
    .. note::
    
             * Remember that the "``_resources``" and the "``resources``" folder are the only place in which
               Genro will search your javascript files, css elements and components.
             * For more information on how insert your resources in the webpages, please check the following section:
               :ref:`webpages_js_requires`, :ref:`webpages_css_requires`, :ref:`webpages_py_requires`.