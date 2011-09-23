.. _gnr_basic_structure:

===============
basic structure
===============
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/gnr/gnr.png
    
    In the ``.gnr`` folder, you have:
    
    * the :ref:`gnr_environment` file; it allows to define the root paths for your
      :ref:`project` folders.
    * the :ref:`gnr_instanceconfig` folder including the :ref:`gnr_instanceconfig_default`
      file; it allows to:
      
      * define the packages you want to use in your :ref:`project`
      * define the name of your database
      * handle the permits of your :ref:`project`
        
    * the :ref:`gnr_siteconfig` folder including the :ref:`gnr_siteconfig_default` file;
      it allows to:
      
      * handle the timeout and the refresh of the connection
      * define your project port
      * import dojo and genro engines