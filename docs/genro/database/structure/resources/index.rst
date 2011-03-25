.. _genro_resources_index:

=============
``resources``
=============

    Define the functionality of the resources!!! add???
    
    The resources are called on :ref:`webpages_webpages` through :ref:`webpages_py_requires`,
    :ref:`webpages_js_requires` and :ref:`webpages_css_requires`. The :mod:`gnr.web.gnrwsgisite`
    module manages the mixin resources.
    
    In the ``resources`` folder you can put every *public* resource (follow the relative links
    for more information about them):
    
    * javascript files
    * :ref:`genro_css`
    * :ref:`genro_components_index`
    
    For *public* we mean a place for the resources that you can use in ANY of the package
    you have into your project.
    
    You can import some resources even from other packages (from outside of your project):
    for doing this, you have to import the name of the package that includes the resource
    you want to use.
    
    .. note:: To import a package, you have to add the package name in your
              :ref:`instances_instanceconfig`
    
    .. image:: ../../../images/structure/structure-resources.png
    
    If you want to keep *private* your resources, you have to put your resources in the
    ``_resources`` folder. For more information, check the :ref:`genro_webpage_resources`
    documentation page.
    
    .. note::
    
             * Remember that the "``_resources``" and the "``resources``" folder are the only place
               in which Genro will search your javascript files, css elements and components.
             * For more information on how insert your resources in the webpages, please check the
               following section: :ref:`webpages_js_requires`, :ref:`webpages_css_requires`,
               :ref:`webpages_py_requires`.