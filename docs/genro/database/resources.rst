.. _genro_resources_index:

=============================
Introduction to the resources
=============================

    add??? Tenere introduzione generale, dividere le cose specifiche delle
    cartelle delle risorse private e pubbliche...

    A ``resources`` folder is thought to speed up your work, because it is
    used to keep all the stuff that you need to use over and over in a Genro
    :ref:`genro_project`. If you put your files in this folder, you can use
    them many times, calling them in your :ref:`webpages_webpages`.
    
    The great feature is that you can define your resources as
    :ref:`genro_public_resource`\s or :ref:`genro_private_resource`\s. Let's give
    now a definition of *private* and *public* resources; in the next sections
    we'll detail the features:
    
    * A *public* resource is a file that you can reuse in ANY project.
    * A *private* resource is a file that you can reuse only in the project in
      which you define them.
      
.. _genro_public_resource:
    
public resource
---------------
    
    **Definition**: a *public* resource is a file that you can reuse in ANY project.
    
    **Description**: to make *public* a resource, you have to create your resources
    files into a ``resources`` folder that is set into this path::
    
        projectName/packages/packageName/resources
        
    where:
    
    * ``projectName`` is the name of your project
    * ``packages`` is the standard :ref:`genro_packages_index` folder
    * ``packageName`` is the name of your package
    * ``resources`` is the folder where you have to put your resources files.
    
    In this image we'll show you the path for your *public* resources:
    
    .. image:: ../../images/structure/public_resources1.png
    
    Example: if you would want to keep in your *public* resources some images, a
    CSS file and some other stuff, your project tree might be the following one:
    
    .. image:: ../../images/structure/public_resources2.png
    
    Where:
    
    * ``my_project`` is the name of your project.
    * ``base`` is the name of your package.
    
    Some notes:
    
    * The ``images`` folder it is not mandatory, but we have created it to keep order
      in the project (we'll put all the images there).
    * The ``tables`` folder is required to use some additional features, like adding
      a batch and adding a print and for the usage of some Genro :ref:`genro_components`\s.
      For more information, check the :ref:`resources_tables` documentation section.
      
    **Usage**: in order to use the *public* resources, you have to:
    
    #. import the name of the package (that includes the resources you want to use)
       into the :ref:`instanceconfig_packages` tag of your :ref:`genro_gnr_instanceconfig`
       file.
       
       .. warning:: don't forget to import your own package, too!
       
       Example: if you need to add the ``agenda``, the ``staff`` and the ``admin`` packages
       to your project, you have to add three tags into your ``<packages>`` tag::
       
         <?xml version='1.0' encoding='UTF-8'?>
         <GenRoBag>
             <packages>
                 <admin />
                 <agenda />
                 <staff />
             </packages>
             <!-- Here lies other instanceconfig tags... -->
         </GenRoBag>
         
       Remember to import your own package, too (if you defined some *public* resources
       in it, obviously): for example, if your package is called ``base``, your
       instanceconfig file will become::
         
         <?xml version='1.0' encoding='UTF-8'?>
          <GenRoBag>
              <packages>
                  <base /> <!-- Hint: keep it as the first package imported, so you
                                can always rapidly check if you have imported your
                                own package or if you forgot it! -->
                  <admin />
                  <agenda />
                  <staff />
              </packages>
              <!-- Here lies other instanceconfig tags... -->
          </GenRoBag>
          
    #. call the resource you need in the :ref:`webpages_webpages` in which you will use
       it through a ``webpages variable``:
       
        * :ref:`webpages_py_requires` for the Python files
        * :ref:`webpages_js_requires` for the Javascript files
        * :ref:`webpages_css_requires` for the CSS files
        
        For more information, check the :ref:`webpages_variables` documentation section.
        
.. _genro_private_resource:
    
private resource
----------------
    
    **Definition**: a *private* resource is a file that you can use only in the
    project in which you define them.
    
    **Description**: to make *private* a resource, you have to create your resources
    files into a ``resources`` folder that is set into the following path::
    
        projectName/resources
        
    where:
    
    * ``projectName`` is the name of your project
    * ``resources`` is the folder where you have to put your resources files.
    
    In this image we'll show you the path for your *private* resources:
    
    .. image:: ../../images/structure/private_resources1.png
    
    Example: if you would want to keep in your *private* resources some images, a
    CSS file and a Javascript file your project tree might be the following one:
    
    .. image:: ../../images/structure/private_resources2.png
    
    Where ``my_project`` is the name of your project - the ``images`` folder it is
    not mandatory, but we have created it to keep order in the project (we'll put
    all our images there).
      
    .. note:: if you read the example of the :ref:`genro_public_resource` section
              you will notice that we added a ``tables`` folder.
              
              That folder MUST be created into your *public* resources.
              
    **Usage**: in order to use the *private* resources, you have to:
    
    #. call the resource you need in the :ref:`webpages_webpages` in which you will use
       it through a ``webpages variable``:
       
        * :ref:`webpages_py_requires` for the Python files
        * :ref:`webpages_js_requires` for the Javascript files
        * :ref:`webpages_css_requires` for the CSS files
        
        For more information, check the :ref:`webpages_variables` documentation section.
        
**Footnotes**:

.. [#] For more information on how to use CSS in Genro, check the :ref:`genro_css` documentation page
.. [#] For more information on Genro components, check the :ref:`genro_components`\s documentation page