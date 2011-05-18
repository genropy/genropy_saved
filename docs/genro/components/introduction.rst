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
    
    A component is a python file that gathers some useful features (classes) that can be used in more
    than one project. Every component can be rewritten in most of its parts (methods) overriding them.
    This ensures the ability to customize a component for your specific purpose.
    
    Components belong to the family of Genro :ref:`genro_intro_resources`.
    
.. _components_location:

Components location
===================
    
    The components MUST be situated in a folder named ``resources``. There are two possibles places
    to put a component:
    
    #. If you place a component at the following path::
        
        packageName/resources
        
       (where ``packageName`` is the name of the package and ``resources`` is a mandatory name for
       the folder), then the component is **private**: this means that anyone can use this component
       only in the project in which it has been created.
       
       The **private** components belong to the family of the :ref:`genro_private_resource`\s.
       
    #. If you place your component at the following path::
        
        projectName/resources
        
       (where ``projectName`` is the name of your project and ``resources`` is a mandatory name for
       the folder), then the component is **public**: this means that anyone can use this component
       in any project.
       
       If you need to import a component follow the instruction of the :ref:`components_requirements`
       section.
       
       The **public** components belong to the family of the :ref:`genro_public_resource`\s.
       
    For more information on *private* and *public* components (that is, *private* and *public*
    resources) please check the :ref:`genro_intro_resources` documentation page.
    
.. _components_requirements:

Components requirements
=======================

    To use a component you have to follow these two instructions:
    
    #. import the package (that includes the component you want to use) in your
       :ref:`instances_instanceconfig` file
       
    #. set in your :ref:`webpages_webpages`\s a requirement: every component
       has to be called through the correct :ref:`webpages_py_requires` webpage variable.
       
       * Syntax::
       
           py_requires = 'fileName:componentClassName'
           
       Where:
       
           * ``fileName`` is the name of the file including the component (it is not important
             to specify its folder, because thorugh the mixin technique Genro searchs within
             all the folder called ``resources`` [#]_)
           * ``componentClassName`` is the name of the component class.
       
       .. note:: In every component's documentation page you fill find the correct syntax for
                 its ``py_requires``
              
    **Example:** if you should need to import a component of the package ``tools`` called... add???
    
    
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
    
    **Tables**:
    
    * :ref:`genro_th`
    
    **add???**
    
    * :ref:`genro_includedview`
    * timetable_dh

**Footnotes**:

.. [#] As you can see in the image, a Genro :ref:`genro_project` is composed by four main folders, that are: :ref:`genro_instances_index`, :ref:`genro_packages_index`, :ref:`genro_resources_index`, :ref:`genro_sites_index` - click on these links for more informations about a project and its subfolders.
.. [#] Obviously, if you create a component please remember to put in a ``resources`` folder! (Check the :ref:`components_location` paragraph for more information on the component positioning)
    