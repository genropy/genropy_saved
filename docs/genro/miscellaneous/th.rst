.. _genro_th:

============
tableHandler
============

    * :ref:`th_introduction`
    * :ref:`th_tables`:
    
        * :ref:`th_firststeps`
        * :ref:`th_table`:
        
            * the :ref:`th_view_class` (methods: :ref:`th_order`, :ref:`th_query`)
            * the :ref:`th_form_class`
            
        * :ref:`th_map`
        * :ref:`th_page`:
        * :ref:`th_form_uses`
    
    * :ref:`th_iv_methods`:
    
        * :ref:`th_border`
        * :ref:`th_dialog`
        * :ref:`th_palette`
        * :ref:`th_plain`
        * :ref:`th_stack`
        
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
    
    Example: if you have to create a table with the registry (in italian , the *anagrafica*)
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

    Now we'll guide you in a "step by step" creation of a tableHandler.
    
    Let's suppose that your project is called ``my_project``. Inside the :ref:`packages_model`
    folder we create a table called ``registry.py`` with all the records you need (name,
    surname, email, and so on).
    
    Now, if we have to reuse a lot of time this table - that is, there are a lot of webpages
    that will use this table - we have to:
    
    #. create a folder called ``resources`` inside the package we are using (in this example
       the package is called ``base``).
    #. Inside the ``resources`` folder just created, we have to create a folder called ``tables``.
    #. Inside the ``tables`` folder, you have to create another folder with the SAME name of the
       table file name: in this example the folder is called ``registry``
    #. Inside the ``registry`` folder you have to create a Python file called ``th_`` +
       ``tableFileName``: in this example the file is called ``th_registry``
       
    Let's check out this figure that sum up all the creation of new folders and files:
    
    .. image:: ../images/th/th.png
    
    Pay attention that for every tableHandler you want to create, you have to repeat
    the point 3 and 4 of the previous list; for example, if you have three tables called
    ``registry.py``, ``staff.py`` and ``auth.py``, you have to create three folders into the
    ``tables`` folder with a ``th_`` file in each folder, as you can see in the following
    image:
    
    .. image:: ../images/th/th2.png
    
.. _th_table:

th_table
--------

    Let's check now the code inside a page with the ``View`` and the ``Form`` classes.
    
    The first line will be::
    
        from gnr.web.gnrbaseclasses import BaseComponent
    
    .. module:: gnr.web.gnrbaseclasses
    
    because the View and the Form classes are derived classes of the :class:`BaseComponent`
    class.
    
.. _th_view_class:

View class
----------
    
    The ``View`` class is used to let the user visualize some fields of its saved records.
    You don't have to insert ALL the fields of your table, but only the fields that you want
    that user could see in the View.
    
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
        
    where ``name``, ``surname`` and ``email`` are three rows of your :ref:`genro_table`.
    
    The main methods you have to insert now are the :ref:`th_order` and the :ref:`th_query`.
    
.. _th_order:

th_order
--------
    
    A method of the :ref:`th_view_class`.
    
    ::
    
        def th_order(self):
            return 'surname'
            
    The ``th_order`` returns a field of your table, and orders the View class
    alphabetically in relation to the field you wrote.
    
.. _th_query:

th_query
--------

    A method of the :ref:`th_view_class`.
    
    ::
    
        def th_query(self):
            return dict(column='surname', op='contains', val='', runOnStart=True)
            
    The ``th_query`` defines the standard query of your page. In particular:
    
    * the ``column`` attribute includes the field of your table through which will be done
      the query
    * the ``op`` attribute is the SQL operator for SQL queries
    * the ``val`` attribute is the string to be queried
    * the ``runOnStart=True`` (by default is ``False``) allow to start a query on page loading
      (if you don't write it user have to click the query button to make the query start)
    
.. _th_form_class:

Form class
----------
    
    The first two lines define the class and the method::
    
        class Form(BaseComponent):
            def th_form(self, form):
            
    Now write the following line::
    
        pane = form.record
        
    (We'll come back later on this one - in the :ref:`th_map` section. For now just know that
    you are focusing the path of your data in the *correct* place)
    
    The next line can be the :ref:`genro_formbuilder` definition [#]_::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    .. _th_map:

tableHandler paths
==================

    In this section you will learn about the path structure of the tableHandler:
    
    .. image:: ../images/th/th_map.png
    
    Let's see the features of this hierarchy:
    
    * **th**: the main level of the tableHandler. Nested to it there are the *form* level
      and the *view* level, that handle respectively the path of the data of the
      :ref:`th_form_class` and :ref:`th_view_class`.
      
      .. warning:: This is very important. At the ``th`` level, the path of the data is::
      
                      .packageName_tableName
                      
                   where ``packageName`` is the name of your package and ``tableName`` is
                   the name of your :ref:`genro_table`. (The dot (``.``) before the
                   ``packageName`` specifies that the path is relative [#]_).
                   You are HERE, so if you need to interact with other levels, remember
                   that your root is ``.packageName_tableName``
      
      In our example, the package name is called ``base`` and the table is ``registry.py``,
      so the path will be ``.base_registry``.
      
    * **form**: this level handles all the data of the :ref:`th_form_class`.
      
      At the ``th/form`` level, the path of the data is::
      
          .packageName_tableName.form
          
      The inner paths of the ``form`` level are built in complete analogy with
      the structure of a Dojo :ref:`genro_bordercontainer`, so the level is
      divided into five regions:
      
      * ``top``
      * ``bottom``
      * ``left``
      * ``right``
      * ``center``
      
      where:
      
      * The ``top`` level includes the title of the view page [#]_ and the :ref:`genro_workdate`.
        
        The ``top`` level has a ``bar`` sublevel: this sublevel contains some query tools
        and some buttons to add or delete records.
        
      * The ``bottom`` level is used to give to user messages (e.g: for right save).
        
        and ``bottom`` level have an additional ``bar``
        level that handle the top bar and the bottom bar.
        
      * The ``left`` level allows the user to perform some useful action (e.g: to configurate
        user view; e.g: to export query results in a ``.xls`` file).
        
      * The ``right`` level is (currently) empty.
        
      * The ``center`` level is used to create more complex structure inside your page.
        We'll come back later to it, in the :ref:`th_form_uses` section.
      
    * **record**: at the ``th/form/record`` level, the path of the data is::
    
        .packageName_tableName.form.record
        
      At this path level lie the data of records.
      
      In our example the path will be ``.base_registry.form.record``.
      
      .. warning:: now you can understand the line we wrote in the previous
                   section (:ref:`th_table`) inside the Form method::
                   
                    pane = form.record
                    
                   Remember that when you have to interact with data you have to go
                   to the ``form.record`` path.
      
    * **view**: add???
    * **grid**: add???
    
.. _th_page:

th_page
=======

    When you build some complex tables, you may need to use both a :ref:`th_table` and a
    th_page. The th_page is a :ref:`webpages_GnrCustomWebPage` that allows you to create
    a much complex ``Form`` class.
    
    .. note:: please call your webpages with the suffix ``_page``. This is a convention
              to keep order in your project (e.g: ``staff_page.py``)
              
    So, if you build a th_page, you have to build anyway a :ref:`th_table` with the
    ``View`` class defined in all its structures, while the ``Form`` class can be
    simply::
    
        class Form(BaseComponent):
            def th_form(self, form):
                pass
                
    because you will handle the View class in the th_page.
    
    To create your th_page, you have to write::
    
        class GnrCustomWebPage(object):
        
    Then you have to specify the :ref:`genro_table` to which this page refers to::
    
        maintable = 'packageName.tableName'
        
    In our example, the package name is ``base`` and the table name is ``registry``, so
    the maintable looks like ``maintable = 'base.registry'``
    
    Then you have to define the correct :ref:`webpages_py_requires`::
    
        py_requires = 'public:TableHandlerMain'
        
    For more informations on ``py_requires``, please check the :ref:`webpages_py_requires`
    documentation section.
    
    Then you may define the following methods::
        
        def pageAuthTags(self, method=None, **kwargs):
            return 'user'
            
        def windowTitle(self):
            return 'Registry'
            
        def barTitle(self):
            return 'Registry'
            
        def tableWriteTags(self):
            return 'user'
            
        def tableDeleteTags(self):
            return 'user'
            
    where:
    
    .. module:: gnr.web._gnrbasewebpage.GnrBaseWebPage
    
    * The pageAuthTags, the tableWriteTags and the tableDeleteTags methods handle
      the permits of the page to see it, write on it and delete records.
      The return string (in the example returns ``user`) allow to define who has
      the permits to act. You can find more information on page permits into the
      :ref:`instanceconfig_authentication` section of the
      :ref:`genro_gnr_instanceconfig` documentation page)
    * The windowTitle and the barTitle define the title and the bar of the page on
      the browser.
      
    After that, we have to define the ``th_form`` method; it replaces the ``th_form``
    method we wrote in the th_table.
    
    The definition line is::
    
        def th_form(self,form,**kwargs):
        
    As we taught to you in the :ref:`th_table` section, the next line is (most of the time!)::
    
        pane = form.record
        
    If you need more information on this line, please check the :ref:`th_map` section.
    
    After that, you have to create your :ref:`genro_form`. The first line is the
    :ref:`genro_formbuilder` definition::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    After that, you can add all your supporting methods you need: for example, you may need
    a onLoading method::
    
        def onLoading(self, record, newrecord, loadingParameters, recInfo):
            if newrecord:
                record['username'] = self.user
                record['day'] = self.workdate
                record['hour'] = datetime.datetime.now().time()
                
    .. _th_form_uses:

``center`` path
---------------

    If you need to use some complex :ref:`genro_layout_index` in your page, like a
    :ref:`genro_tabcontainer`, you have to pass from the ``form.center`` path. Example::
    
        tc = form.center.tabContainer()
        
        bc = tc.borderContainer(datapath='.record', title='Profilo')
        other = tc.contentPane(title='Other things')
        altro.numbertextbox(value='^.numerobusatto',default=36)
        
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='1px',height='40%')
        top.div('!!Record di anagrafica',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(dbtable='sw_base.anagrafica',margin_left='10px',margin_top='1em',
                             width='370px',datapath='.@anagrafica_id',cols=2)
                             
    .. _th_iv_methods:

includedView methods
====================

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
    
**Footnotes**:

.. [#] The :ref:`genro_standardtable_index` is the the most known name of the component that handled tableHandler until now.
.. [#] The :ref:`genro_formbuilder` allows to create in a simple way a :ref:`genro_form`. Follow the links for more informations.
.. [#] For more information on absolute and relative paths, check the :ref:`genro_datapath` documentation page.
.. [#] The title of the view page is taken from the :ref:`genro_name_long` of the :ref:`genro_table` to which the current webpage refers to.
