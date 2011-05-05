.. _genro_th:

============
tableHandler
============

    .. note:: Welcome!
              
              This is a temporary page to explain the new ``th`` (tableHandler) class.
              This page will change progressively with method changements, until the
              class will become stable.
              
    * :ref:`th_introduction`
    * :ref:`th_tables`
    * :ref:`th_page`:
    
        * :ref:`page_py_requires`
        
    * :ref:`th_methods`:
    
        * :ref:`th_border`
        * :ref:`th_dialog`
        * :ref:`th_palette`
        * :ref:`th_plain`
        * :ref:`th_stack`
        
    * :ref:`th_old_new`:
    
        * :ref:`old_new_index`
        * :ref:`old_new_resources`
    
.. _th_introduction:

Introduction
============

    The tableHandler is the Genro way to handle data visualization and data entry [#]_.
    
    The tableHandler is structured in two main classes:
    
    * the View class, that allows to manage data visualization
    * the Form class, that allows to manage data entry
    
    The novelty now is that you can create your tableHandlers into the ``resources`` folder
    of your :ref:`genro_project`\s. This fact allows to reuse the tableHandlers you created
    in more than a webpage.
    
    Example: if you have to create a table with the registry (in italian , the "anagrafica")
    of a society, a registry of the staff, a registry of society clients (and so on) you can
    create a single resource that you can reuse every time you need it. Cool, isn't it?
    
    In the following sections we try to explain all the info you need to make the new
    tableHandler works.
    
.. _th_tables:

Creation of a tableHandler resource
===================================

    Let's continue with the example of the previous section (the "registry" one).
    
    Let's suppose that your project is called ``my_project``. Inside the :ref:`packages_model`
    folder we create a table called ``registry.py`` with all the records you need (name,
    surname, email, and so on).
    
    Now, if we have to reuse a lot of time this table - that is, there are a lot of webpages
    that will use this table - we have to:
    
    #. create a folder called ``resources`` inside the package we are using (in this example
       the package is called ``base``).
    #. Inside the ``resources`` folder just created, we have to create a folder called ``tables``.
    #. Inside the ``tables`` folder, you have to create a folder with the SAME name of the
       table file name (we're almost done!): in this example the folder is called ``registry``
    #. Inside the ``registry`` folder you have to create a Python file called ``th_`` +
       ``tableFileName``: in this example the file is called ``th_registry``
       
    Let's check out this figure that sum up all the creation of new folders and files:
    
    .. image:: ../images/th.png
    
    Pay attention that for every tableHandler you want to create, you have to repeat
    the point 3 and 4 of the previous list.
    
    Example: if you have three tables called ``registry.py``, ``staff.py`` and ``auth.py``,
    you have to create three folders into the ``tables`` folder with a ``th_`` file in each
    folder:
    
    .. image:: ../images/th2.png
    
.. _th_page:

webpages
========

    add???

.. _page_py_requires:

``py_requires``
---------------
    
    In order to use the ``th`` component in your :ref:`webpages_webpages`, please add
    the following ``py_requires``::
    
        py_requires = "public:TableHandlerMain"
        
    For more informations on ``py_requires``, please check the :ref:`webpages_py_requires`
    documentation section.
    
.. _th_methods:

th methods
==========

    In this section we explain all the methods of the ``th`` resource.
    
.. _th_border:

th_borderTableHandler
---------------------

    .. method:: th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,loadEvent='onSelected',readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,**kwargs)
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``False``
    * *widget_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *loadEvent*: add???. Default value is ``'onSelected'``
    * *readOnly*: add???. Default value is ``False``
    
.. _th_dialog:

th_dialogTableHandler
---------------------

    .. method:: th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,[**kwargs])
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``None``
    * *dialog_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *readOnly*: add???. Default value is ``False``
    
.. _th_palette:

th_paletteTableHandler
----------------------

    .. method:: th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,palette_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``False``
    * *palette_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *readOnly*: add???. Default value is ``False``
    
.. _th_plain:

th_plainTableHandler
--------------------

    .. method:: th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=True,**kwargs)
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``False``
    * *widget_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *readOnly*: add???. Default value is ``True``
    
    This method has only the View, not the Form.
    
.. _th_stack:

th_stackTableHandler
--------------------

    .. method:: th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    Where:
    
    * *pane*: add???
    * *nodeId*: add???. Default value is ``None``
    * *table*: add???. Default value is ``None``
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *viewResource*: add???. Default value is ``None``
    * *formInIframe*: add???. Default value is ``False``
    * *widget_kwargs*: add???. Default value is ``None``
    * *reloader*: add???. Default value is ``None``
    * *default_kwargs*: add???. Default value is ``None``
    * *readOnly*: add???. Default value is ``False``
    
.. _th_old_new:

convert your project into the new mode
======================================

    .. warning:: completely to do!! (add???)
    
    This section wants to explain what modifies you have to do to pass from the old mode
    to the new one.
    
.. _old_new_index:

index
-----

    add???

.. _old_new_resources:
    
resources
---------

    if you have some ``_resources`` folders in your webpages, please move them into add???
    
**Footnotes**:

.. [#] The :ref:`genro_standardtable_index` is the the most known name of the component that handled tableHandler until now.
    