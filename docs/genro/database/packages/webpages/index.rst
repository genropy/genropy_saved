.. _packages_webpages:

============
``webpages``
============
    
    *Last page update*: |today|
    
    .. image:: ../../../_images/projects/packages/webpages.png
    
    * :ref:`webpages_intro`
    * :ref:`webpages_section_index`
    
.. _webpages_intro:

introduction
============

    In the ``webpages`` folder you can keep all your :ref:`webpages <webpage>`.
    
    In Genropy, a webpage is written as a Python file; in particular, the class that
    handles all the stuff you need for a webpage is the :ref:`gnrcustomwebpage`
    class - in the next page we'll describe this class.
    
    When you create a :ref:`project`, you (probably) will create the following webpages:
    
    #. A login page. For more information, check the :ref:`methods_loginUrl` section
    #. An index page. You can build your own index, or you can use a
       :ref:`component <components>` that handles it, like the :ref:`frameindex`.
       
       .. note:: by default, the name of the first page loaded has to be ``index.py``. You can
                 change this default using the *homepage* attribute of the :ref:`siteconfig_wsgi`
                 tag of the :ref:`gnr_siteconfig` file
                 
    #. A set of webpages related to some database :ref:`tables <table>`.
       
       .. note:: when you create a webpage that is related to a :ref:`table`,
                 please name it following this convention::
                 
                   tableName + ``_page.py``
                   
                 example: if you have a table called ``staff.py``, call the webpage
                 ``staff_page.py``.
                 
                 This convention allows to keep order in your project.
    
    #. A set of webpages not related to database tables used for other services

.. _webpages_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    
    webpages