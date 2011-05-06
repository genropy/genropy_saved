.. _genro_th:

============
tableHandler
============

    .. note:: Welcome!
              
              This is a temporary page to explain the new ``th`` (tableHandler) class.
              This page will change progressively with method changements, until the
              class will become stable.
              
    * :ref:`th_introduction`
    * :ref:`th_tables`:
    
        * :ref:`th_firststeps`
        * :ref:`th_page`
        * :ref:`th_map`
        
    * :ref:`th_webpage`:
    
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

.. _th_firststeps:

first steps
-----------

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
    
    .. image:: ../images/th/th.png
    
    Pay attention that for every tableHandler you want to create, you have to repeat
    the point 3 and 4 of the previous list.
    
    Example: if you have three tables called ``registry.py``, ``staff.py`` and ``auth.py``,
    you have to create three folders into the ``tables`` folder with a ``th_`` file in each
    folder:
    
    .. image:: ../images/th/th2.png
    
    In the next section we check the code inside a ``th_page``
    
.. _th_page:

creation of a ``th_page``
-------------------------

    Let's check now the code inside a ``th_page``.
    
    The first line will be::
    
        from gnr.web.gnrbaseclasses import BaseComponent
        
    because the View and the Form classes are derived classes of the ``BaseComponent`` class.
        
    We introduce now the ``View`` class. The ``View`` class is used to let the user visualize
    some fields of its saved records. You don't have to insert ALL the fields of your table,
    but only the fields that you want that user could see in the View.
    
    The first three lines define:
    
    * the class name
    * the method name (th_struct)
    * the creation of the :ref:`genro_struct` with its rows::
    
        class View(BaseComponent):
            def th_struct(self,struct):
                r = struct.view().rows()
                
    The next lines define the struct rows. Usually you have to use some
    :ref:`genro_fieldcell`\s, like in this example::
        
        r.fieldcell('name', width='12em')
        r.fieldcell('surname', width='12em')
        r.fieldcell('email', width='15em')
        
    where ``name``, ``surname`` and ``email`` are three rows of your :ref:`packages_model`.
                
    The main methods you have to insert now are the ``th_order`` and the ``th_query``::
                
        def th_order(self):
            return 'surname'
            
        def th_query(self):
            return dict(column='surname', op='contains', val='', runOnStart=True)
            
    The ``th_order`` returns a field of your table, and orders the View class
    alphabetically in relation to the field you wrote.
    
    The ``th_query`` defines the standard query of your page. In particular:
    
    * the ``column`` attribute includes the field of your table through which will be done
      the query
    * the ``op`` attribute is the SQL operator for SQL queries
    * the ``val`` attribute is the string to be queried
    * the ``runOnStart=True`` (by default is ``False``) allow to start a query on page loading
      (if you don't write it user have to click the query button to make the query start)
      
    Now we will introduce the Form class. The first two lines define the class and the method::
    
        class Form(BaseComponent):
            def th_form(self, form):
            
    At this point usually you will write a short but very dense row::
    
        pane = form.record
        
    We'll come back later on this one (in the :ref:`th_map` section). For now just know that
    you are focusing the path of your data in the "right" place.
    
    After that, you have to create your :ref:`genro_form_index`. The first line is the
    :ref:`genro_formbuilder` definition::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    This concludes this simple tutorial for the ``th_page``.
        
    .. _th_map:

map
===

    In this image we map the structure of the th inner paths:
    
    .. image:: ../images/th/th_map.png
    
    **th**: at the ``th`` level, the path of the data is::
    
        .packageName_tableName
        
    The dot (``.``) specify that the path is relative (you can find more information on
    absolute and relative path in the :ref:`genro_datapath` documentation page).
    
    In our example, the package name is ``base`` and the table is (for example) ``registry``,
    so the path will be ``.base_registry``.
    
    **form**: at the ``th/form`` level, the path of the data is::
    
        .packageName_tableName.form
        
    In our example the path will be ``.base_registry.form``.
    
    **record**: at the ``th/form/record`` level, the path of the data is::
    
        .packageName_tableName.form.record
        
    At this path level lie the data of records.
    
    In our example the path will be ``.base_registry.form.record``.
    
    Now you can understand the line we wrote in the previous section (:ref:`th_page`)
    inside the Form method::
    
        pane = form.record
        
    The rule is:
    
    .. note:: when you have to interact with data you have to go to the ``form.record`` path
        
    In the next section we explain to you when you have to use the ``form`` path (without
    arriving to the ``record`` path).
    
.. _th_form_uses:

The ``form`` path
=================

    add???
    
.. _th_webpage:

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

    In this section we explain all the methods of the ``th`` class.
    
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
    * *viewRegion*: add?. Default value is ``None``
    * *formRegion*: add?. Default value is ``None``
    * *vpane_kwargs*: add?. Default value is ``None``
    * *fpane_kwargs*: add?. Default value is ``None``
    
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
    