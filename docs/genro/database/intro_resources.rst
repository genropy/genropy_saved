.. _genro_intro_resources:

=========
resources
=========
    
    *Last page update*: |today|
    
    A ``resources`` folder is thought to speed up your work, because it is used to
    keep all the stuff that you need to use over and over in a Genro :ref:`genro_project`.
    
    We'll call *resources* all the files that you keep in a ``resources`` folder.
    In particular, your *resources* can be:
    
    * javascript and CSS files: you probably know everything about javascript and css.
      What you don't know is how they interact with Genro. For more information, check
      the :ref:`genro_css` and the :ref:`genro_javascript` documentation page
    * :ref:`genro_component`\s, or, more generally, other Python modules
    
    You can define your resources as *public resources* or *private resources*:
    
    * A :ref:`genro_public_resource` is a file that can be used in ANY project.
    * A :ref:`genro_private_resource` is a file that can be used only in the
      project in which the resource has been defined.
      
.. _genro_public_resource:

public resource
---------------
    
    **Definition**: a *public* resource is a file that can be used in ANY project.
    
    **Description**: to make *public* a resource, you have to create your resources
    files into a ``resources`` folder that is set into this path::
    
        projectName/packages/packageName/resources
        
    where ``projectName`` is the name of your project, :ref:`genro_packages_index` is
    the folder that contains the packages, ``packageName`` is the name of your package,
    ``resources`` is the folder where you have to put your resources files.
    
        **Example:** If you have a project called ``my_project`` and a package
        called ``base``, then you will have this tree for your *public* resources:
        
        .. image:: ../_images/projects/resources/public_resources1.png
        
        Now, if you would want to keep in your *public* resources some images, a CSS
        file and some other stuff, your project tree might be the following one:
        
        .. image:: ../_images/projects/resources/public_resources2.png
        
        Some notes:
        
        * The ``images`` folder it is not mandatory, but we have created it to keep order
          in the project (we'll put all the images there). With the same reason you could
          create a folder for your javascript files, one folder for your python modules
          and one folder for your CSS files.
        * The ``tables`` folder is required to use some additional features, like:
        
            * adding some batches
            * adding some print features
            * usage of the :ref:`genro_th` component
            
          For more information on this folder, check the :ref:`resources_tables`
          documentation section.
          
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
       
        * :ref:`webpages_py_requires` for Genro :ref:`genro_component`\s and other Python modules
        * :ref:`webpages_js_requires` for the javascript files
        * :ref:`webpages_css_requires` for the CSS files
        
        For more information (and examples) on ``webpages variables``, check the
        :ref:`webpages_variables` documentation section.
        
.. _genro_private_resource:
    
private resource
----------------
    
    **Definition**: a *private* resource is a file that can be used only in the
    project in which the resource has been defined.
    
    **Description**: to make *private* a resource, you have to create your resources
    files into a ``resources`` folder that is set into the following path::
    
        projectName/resources
        
    where ``projectName`` is the name of your project and ``resources`` is the folder
    where you have to put your resources files (as well as one of the four main
    sub-folders of your project)
    
        **Example:** If you have a project called ``my_project`` then you will have
        this tree for your *private* resources:
        
        .. image:: ../_images/projects/resources/private_resources1.png
        
        Now, if you would want to keep in your *private* resources some images, a CSS
        file and a javascript file, your project tree might be the following one:
        
        .. image:: ../_images/projects/resources/private_resources2.png
        
        Where ``my_project`` is the name of your project - the ``images`` folder it is
        not mandatory, but we have created it to keep order in the project (we'll put
        all the images there). With the same reason you could create a folder for your
        javascript files, one folder for your python modules and one folder for your
        CSS files.
        
        .. note:: if you read the example of the :ref:`genro_public_resource` section
                  you will notice that we added a ``tables`` folder.
                  
                  That folder MUST be created into your *public* resources.
                  
    **Usage**: in order to use the *private* resources, you have to:
    
    #. call the resource you need in the :ref:`webpages_webpages` in which you will use
       it through a ``webpages variable``:
       
        * :ref:`webpages_py_requires` for the Python files
        * :ref:`webpages_js_requires` for the javascript files
        * :ref:`webpages_css_requires` for the CSS files
        
        For more information, check the :ref:`webpages_variables` documentation section.
        
**Footnotes**:

.. [#] For more information on how to use CSS in Genro, check the :ref:`genro_css` documentation page
.. [#] For more information on Genro components, check the :ref:`genro_component`\s documentation page