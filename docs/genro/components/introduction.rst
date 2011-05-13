.. _genro_components_introduction:

============
Introduction
============

    * :ref:`components_def`
    * :ref:`components_location`
    * :ref:`components_active_passive`
    * :ref:`components_requirements`
    * :ref:`components_list`
    
.. _components_def:

Definition
==========
    
    A component is a file that gathers some useful features (classes) that can be used in more
    than one project. Every component can be rewritten in most of its parts (methods) overriding some
    of its portions. This ensures the ability to customize a component for your specific purpose.
    
.. _components_location:

Components location
===================
    
    The components MUST be situated in folders named ``resources``: it doesn't matter where these
    folders are, because Genro searchs components in every folder of the code using mixin. However,
    for keeping a reasonable level of order, every ``resources`` folder is kept into a project
    folder as one of its primary subfolder.
    
    If you have a project called ``myproject`` and a component called ``my_component.py``, you have
    to put your component in the :ref:`genro_resources_index` folder of your Genro :ref:`genro_project` [#]_:
    
    .. image:: ../images/components/mycomponent.png
    
    Genro provides another possible place for components::
    
        projectName/packages/packageName/webpages/_resouces
    
    where ``projectName`` is the name of your project and ``packageName`` is the name of your package.
    
    .. image:: ../images/components/mycomponent2.png
    
    In this example, the ``projectName`` and the ``packageName`` are both called ``myproject``.
    
    BUT, if you place your component in a ``_resources`` folder, it can be used only in the specific
    package that contains the ``_resources`` folder. For more information, check the
    :ref:`genro_resources_index` documentation page.
    
.. _components_requirements:

Components requirements
=======================

    To use a component you have to set in your :ref:`webpages_webpages`\s a requirement: every component
    has to be called through the correct :ref:`webpages_py_requires` webpage variable.
    
    * Syntax::
    
        py_requires = 'fileName:componentClassName'
        
    Where:
    
        * ``fileName`` is the name of the file including the component (it is not important to specify its
          folder, because thorugh the mixin technique Genro searchs within all the folder called ``resources`` [#]_)
        * ``componentClassName`` is the name of the component class.
    
    .. note:: In every component's documentation page you fill find the correct syntax for its ``py_requires``
    
.. _components_active_passive:

Active or passive component
===========================

    We can distighuish between active and passive component:
    
    * **active component**: a component that overrides the main method.
    * **passive component**: a component that doesn't have its own main method.
    
    .. note:: Usually, a component is *active* OR *passive*, but this is merely a convention.
              You can create a component that is both *active* and *passive*.

.. _components_list:

List of all the components
==========================

    **Dialogs**:
    
    * iframedialog
    * simpledialog
    * :ref:`genro_recorddialog`
    
    **Login components**:
    
    * :ref:`genro_login_component`
    
    **Tables**:
    
    * :ref:`genro_th`
    
    **add???**
    
    * :ref:`genro_includedview`
    * :ref:`genro_selectionhandler`
    * multiselect
    * timetable_dh

**Footnotes**:

.. [#] As you can see in the image, a Genro :ref:`genro_project` is composed by four main folders, that are: :ref:`genro_instances_index`, :ref:`genro_packages_index`, :ref:`genro_resources_index`, :ref:`genro_sites_index` - click on these links for more informations about a project and its subfolders.
.. [#] Obviously, if you create a component please remember to put in a ``resources`` folder! (Check the :ref:`components_location` paragraph for more information on the component positioning)
    