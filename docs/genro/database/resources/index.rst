.. _genro_resources_index:

=============
``resources``
=============

    A ``resources`` folder keeps all the common stuff that can be used both
    in your project and in other projects.
    
    In particular, you can keep:
    
    * Javascript files
    * CSS files [#]_
    * Python files including components [#]_ or, in general, other classes or methods
    
    To use a resource file you have to:
    
    * place it into a ``resources`` folder
    * call it in the webpage in which you need it through a :ref:`webpages_variables`:
        
        * :ref:`webpages_py_requires` for the Python files
        * :ref:`webpages_js_requires` for the Javascript files
        * :ref:`webpages_css_requires` for the CSS files
    
.. _resources_public_private:

public and private resources
============================
    
    As you should know, every project is composed by 4 main folders, that are:
    
    * the :ref:`genro_instances_index` folder
    * the :ref:`genro_packages_index` folder
    * the ``resources`` folder
    * the :ref:`genro_sites_index` folder
    
    add??? CORRECT!! If you define your resources into the ``resources`` folder, your resources will be
    *public*, but if you define them into the ``_resources`` folder (you have to create
    it into your ``packages/webpages`` folder) your resources will be *private*:
    
    .. image:: ../../images/structure/structure-resources.png
    
    add??? change the image!! (no more "_resources"...)
    
.. _genro_public_resource:
    
public resource
---------------
    
    add??? CORRECT!!
    
    A *public* resource is a file included in the ``resources`` folder that you can use
    in ANY of the package you have into your project and that you can use in any project.
    
.. _genro_private_resource:
    
private resource
----------------
    
    add??? CORRECT!!
    
    A *private* resource is a file included in the ``_resources`` folder that you can
    use only in the package in which they are defined.
    
    add??? CORRECT!!
    So, a *public* resource can be imported from any other project you have. Vice versa, you
    can import any *public* resources from any other projects into your project.
    For doing this, you have to import the name of the package that includes the resource
    you want to use, adding its name into the :ref:`instanceconfig_packages` tag of your
    :ref:`instances_instanceconfig`
    
    .. note::
    
             * Remember that the "``_resources``" and the "``resources``" folder
               are the only place in which Genro will search your resources.
             * For more information on how insert the resources in your webpages,
               please check the following section: :ref:`webpages_css_requires`,
               :ref:`webpages_js_requires`, :ref:`webpages_py_requires`.
               
**Footnotes**:

.. [#] For more information on how to use CSS in Genro, check the :ref:`genro_css` documentation page
.. [#] For more information on Genro components, check the :ref:`genro_components_index`\s documentation page