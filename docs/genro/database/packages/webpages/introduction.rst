.. _webpages_intro:

============
``webpages``
============

    .. image:: ../../../images/projects/packages/webpages.png
    
    In the ``webpages`` folder you can keep all your :ref:`webpages_webpages`\s.
    
    In Genropy, a webpage is written as a Python file; in particular, the class that
    handles all the stuff you need for a webpage is the :ref:`webpages_GnrCustomWebPage`
    class - in the next documentation page we'll describe this class.
    
    When you create a :ref:`genro_project`, you (probably) will have the following webpages:
    
    #. An ``index.py`` webpage (the first page loaded in your site). You can build
       your own index, or you can use a :ref:`genro_component` that handles it: the
       :ref:`genro_frameindex`.
    #. A set of webpages related to some database :ref:`genro_table`\s.
       
       .. note:: when you create a webpage that is related to a :ref:`genro_table`,
                 please name it following this convention::
                 
                   tableName + ``_page.py``
                   
                 example: if you have a table called ``staff.py``, call the webpage
                 ``staff_page.py``.
                 
                 This convention allows to keep order in your project.
    
    #. A set of webpages not related to database tables used for other services (login...)