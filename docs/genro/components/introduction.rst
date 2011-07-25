.. _genro_components_introduction:

============
introduction
============
    
    *Last page update*: |today|
    
    * :ref:`components_def`
    * :ref:`components_location`
    * :ref:`components_active_passive`
    * :ref:`components_requirements`
    
.. _components_def:

definition
==========
    
    A component is a python file that gathers some useful features (classes) that can be used in more
    than one project. Every component can be rewritten in most of its parts (methods) overriding them.
    This ensures the ability to customize a component for your specific purpose.
    
    Components belong to the family of Genro :ref:`genro_intro_resources`.
    
.. _components_location:

components location
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
        
       (where ``projectName`` is the name of the project in which you put the component and
       ``resources`` is a mandatory name for the folder), then the component is **public**:
       this means that anyone can use this component in any project.
       
       The **public** components belong to the family of the :ref:`genro_public_resource`\s.
       
       .. warning:: to use a *public* component, you have to specify some requirements.
                    Please read the :ref:`components_requirements` for more information.
                    
    For more information on *private* and *public* components (that is, *private* and *public*
    resources) please check the :ref:`genro_intro_resources` documentation page.
    
.. _components_requirements:

components requirements
=======================

    To use a component you have to follow these two instructions:
    
    #. import the name of the package that includes the component you want
       to use in the :ref:`instanceconfig_packages` tag of your
       :ref:`instances_instanceconfig` file (for more information, check the
       :ref:`instanceconfig_packages` documentation section)
       
       .. note:: this step is optionally if the component you want to import is a
                 :ref:`components_standard`
                 
    #. set in your :ref:`webpages_webpages`\s a requirement: every component
       has to be called through the correct :ref:`webpages_py_requires` webpage variable.
       
       .. note:: In every component's documentation page you fill find the correct syntax for
                 its ``py_requires`` and the name of the package you have to import.
                 
       * **py_requires syntax**::
       
           py_requires = 'folderName/fileName:componentClassName'
           
         Where:
         
         * ``folderName`` is the name of the folder that includes the file with the component
           you need.
         * ``fileName`` is the name of the file including the component (without its
           ``.py`` suffix)
         * ``componentClassName`` is the name of the python class of the component.
         
         .. note:: You should also know that:
                    
                   #. If you need to import all the classes of a component, the syntax becomes::
                      
                         py_requires = 'folderName/fileName'
                         
                   #. You can omit the "``folderName``" if the component is placed at the first
                      level of a :ref:`genro_intro_resources` folder of an imported package.
                      
                      Viceversa, if the component lives in a nested level of a resources folder you
                      have to specify its path.
                      
                         **Example**:  if you need the "``Public``" class of a component called
                         "``public.py``" that lives at the following path::
                         
                             ~/yourRootPathForGenro/genro/.../resources/public.py
                             
                         then your "``py_requires``" will be::
                         
                             py_requires = 'public:Public'
                             
                         **Example**: if you need the "``Power``" class of a component called
                         "``yourcomponent.py``" that lives at the following path::
                         
                             ~/yourRootPathForGenro/genro/.../resources/power_components/yourcomponent.py
                             
                         then your "``py_requires``" will be::
                         
                             py_requires = 'power_components/yourcomponent:Power'
                             
.. _components_standard:

standard component
------------------

    **Definition**: We define a standard component as a component that live in the following
    path::
    
        GNRHOME/resources
        
    .. warning:: for the standard components you don't need to import a package:
                 the package importation is automatically handled in your
                 :ref:`gnr_environment` file (if you have correctly configured the file!)
                 
                 To learn how to configure the ``environment.xml`` file, check the
                 :ref:`environment_resources_components` documentation section.
                 
    .. note:: Remeber to import the proper component's :ref:`webpages_py_requires`.
                 
    .. note:: in every component's documentation page you will find if the component is
              standard.
                 
    .. _components_active_passive:

active or passive components
============================

    We can distighuish between *active* and *passive* components.
    
    Usually, a component is *active* OR *passive*, but this is merely a convention.
    You can create a component that is both *active* and *passive*.
    
    .. note:: in every component's documentation page you will find if the component
              is *active* or *passive*.
    
.. _components_active:
    
active component
----------------
    
    The active component is a component that overrides the main method.
    
.. _components_passive:
    
passive component
-----------------
    
    The passive component is a component that doesn't have its own main method, so you
    have to define your own *main* method in your :ref:`webpages_webpages`.        