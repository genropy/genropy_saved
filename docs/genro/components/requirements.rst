.. _components_requirements:

=======================
components requirements
=======================

    *Last page update*: |today|
    
    * :ref:`components_requirements_intro`
    * :ref:`components_standard`
    * :ref:`components_active_passive`
    
.. _components_requirements_intro:

introduction
============

    To use a component you have to follow these two instructions:
    
    #. import the name of the package that includes the component you want
       to use in the :ref:`instanceconfig_packages` tag of your
       :ref:`instances_instanceconfig` file (for more information, check the
       :ref:`instanceconfig_packages` section)
       
       .. note:: this step is optionally if the component you want to import is a
                 :ref:`components_standard`
                 
    #. set in your :ref:`webpages <webpages_webpages>` a requirement: every component
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
                      level of a :ref:`intro_resources` folder of an imported package.
                      
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
==================

    **Definition**: We define a standard component as a component that live in the following
    path::
    
        GNRHOME/resources
        
    .. warning:: for the standard components you don't need to import a package:
                 the package importation is automatically handled in your
                 :ref:`gnr_environment` file (if you have correctly configured the file!)
                 
                 To learn how to configure the ``environment.xml`` file, check the
                 :ref:`environment_resources_components` section.
                 
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
