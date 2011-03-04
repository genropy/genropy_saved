.. _genro_components_introduction:

==============================
Introduction to the components
==============================

    * :ref:`components_def`
    * :ref:`components_location`
    * :ref:`components_active_passive`
    * :ref:`components_requirements`
    * :ref:`components_list`
    
.. _components_def:

Definition
==========
    
    .. module:: gnr.web.gnrwebpage
    
    A component is a tool that gathers some useful features that can be used in more than one project. Every component can be rewritten in most of its part (method) overriding some of its portions, ensuring the ability to customize for your particular purpose.
    
    A component is built through the :class:`BaseComponent` class
    
.. _components_location:

Components location
===================
    
    The components MUST be situated in some folders named ``resources``: it doesn't matter where these folders are, because the program search the component in every folder of the code using the mixin. However, for keeping a reasonable level of order, every ``resources`` folder is kept into a project folder as one of its primary subfolder.
    
    If we suppose to have a project called ``myproject`` and a resource called (guess what?) ``my_component``, you will find your component right here:
    
    .. image:: ../images/components/mycomponent.png
    
    (As you can see in the image, a Genro :ref:`genro_structure_mainproject` is composed by four main folders, that are: :ref:`genro_instances_index`, :ref:`genro_packages_index`, :ref:`genro_resources_index`, :ref:`genro_sites_index` - click on them for more informations about a project and its folders)
    
    Genro provides another possible place for components::
    
        projectName/packages/packageName/webpages/_resouces
    
    .. image:: ../images/components/mycomponent2.png
    
    where ``projectName`` is the name of your project and ``packageName`` is the name of your package.
    
    BUT, if you place your component in a ``_resources`` folder, it can be used only in your project (that is, ONLY in any one of your packages that belong to that project.)
    
.. _components_requirements:

Components requirements
=======================

    To use a component you have to set in your :ref:`webpages_webpages`\s some requirements: every component has to be called through the ``py_requires``.
    
    The general syntax is::
    
        py_requires = 'fileName:componentClassName'
        
    Where:
    
        * ``fileName`` is the name of the file including the component (it is not important to specify its folder, because thorugh the mixin technique Genro searchs within all the folder called ``resources`` [#]_)
        * ``componentClassName`` is the name of the component class.
    
    .. note:: In every component's documentation page you fill find the correct syntax for the corresponding component (that is, its ``fileName`` and its ``componentClassName``)
    
.. _components_active_passive:

Active and passive components
=============================

    We can distighuish between active and passive components:
    
    * **Active components**: the components that override the main method.
    
    * **Passive components**: the components that doesn't have their own main method.
    
    Usually, a single component is *active* OR *passive*, but this is merely our convention. You can create a component that is BOTH *active* and *passive*.

.. _components_list:

List of all the components
==========================

    For a complete components reference list, please check the :ref:`genro_maturity_matrix` page

**Footnotes**:

.. [#] Obviously, if you create a component please remember to put in the right place! (Check the :ref:`components_location` paragraph for more information on the component positioning)
    