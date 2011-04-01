.. _genro_resources_index:

=============
``resources``
=============

    The ``resources`` folder keeps all the common stuff of your project. If you define
    something in this folder, you can use it anywhere in your project.
    
    In particular, you can keep:
    
    * Javascript files
    * CSS files [#]_
    * Python files including components [#]_ or, in general, other classes or methods
    
    To use a resource file you have to:
    
    * place it into your ``resources`` folder
    * call it in your webpage through the :ref:`webpages_py_requires`, :ref:`webpages_js_requires`
      and :ref:`webpages_css_requires` webpage variables [#]_.
    
.. _resources_public_private:

public and private resources
----------------------------
    
    As you should know, every project is composed by 4 main folders, that are:
    
    * the :ref:`genro_instances_index` folder
    * the :ref:`genro_packages_index` folder
    * the :ref:`genro_resources_index` folder
    * the :ref:`genro_sites_index` folder
    
    If you define your resources into the ``resources`` folder, your resources will be
    *public*, but if you define them into the ``_resources`` folder (you have to create it
    into your ``packages/webpages`` folder) your resources will be *private*:
    
    .. image:: ../../images/structure/structure-resources.png
    
    * If you define your resources into the ``resources`` folder your resources are
      *public*, so you can use them in ANY of the package you have into your project.
    * If you define your resources into the ``_resources`` folder your resources are
      *private*, so you can use them only in the package in which they are defined.
    
    A *public* resource can be imported from any other project you have. Vice versa, you
    can import any *public* resources from any other projects into your project.
    For doing this, you have to import the name of the package that includes the resource
    you want to use, adding its name into your :ref:`instances_instanceconfig`
    
    .. note::
    
             * Remember that the "``_resources``" and the "``resources``" folder are the only place
               in which Genro will search your resources.
             * For more information on how insert the resources in your webpages, please check the
               following section: :ref:`webpages_css_requires`, :ref:`webpages_js_requires`,
               :ref:`webpages_py_requires`.
               
**Footnotes**:

.. [#] For more information on how to use CSS in Genro, check the :ref:`genro_css` documentation page
.. [#] For more information on Genro components, check the :ref:`genro_components_index` documentation page
.. [#] The :mod:`gnr.web.gnrwsgisite` module manages the mixin resources.