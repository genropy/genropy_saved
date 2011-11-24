.. _components_location:

===================
components location
===================

    *Last page update*: |today|
    
    The components MUST be situated in a folder named ``resources``. There are two possibles places
    to put a component:
    
    #. If you place a component at the following path::
        
        packageName/resources
        
       (where ``packageName`` is the name of the package and ``resources`` is a mandatory name for
       the folder), then the component is **private**: this means that anyone can use this component
       only in the project in which it has been created.
       
       The **private** components belong to the family of the :ref:`private resources <private_resource>`.
       
    #. If you place your component at the following path::
        
        projectName/resources
        
       (where ``projectName`` is the name of the project in which you put the component and
       ``resources`` is a mandatory name for the folder), then the component is **public**:
       this means that anyone can use this component in any project.
       
       The **public** components belong to the family of the :ref:`public resources <public_resource>`.
       
       .. warning:: to use a *public* component, you have to specify some requirements.
                    Please read the :ref:`cr` for more information.
                    
    For more information on *private* and *public* components (that is, *private* and *public*
    resources) please check the :ref:`intro_resources` page