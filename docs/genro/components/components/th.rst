.. _genro_th:

============
tableHandler
============

    .. note:: it is a :ref:`components_standard`.
              
    * :ref:`th_introduction`
    * :ref:`th_map`
    * :ref:`th_firststeps`
    * :ref:`th_resource_page`:
    
        * the :ref:`th_view_class` (methods: :ref:`th_order`, :ref:`th_query`)
        * the :ref:`th_form_class`
        
    * :ref:`th_webpage`:
    
        * :ref:`th_py_requires`
        * :ref:`th_webpage_methods`
        * :ref:`th_webpage_th_form`
        * :ref:`th_form_center_path`
    
    * :ref:`th_types`:
    
        * :ref:`types_py_requires`
        * :ref:`types_common_attributes`
        
        * :ref:`th_border`
        * :ref:`th_dialog`
        * :ref:`th_palette`
        * :ref:`th_plain`
        * :ref:`th_stack`
        
    * :ref:`th_iframe_types`
    
        * :ref:`th_linker`
        * :ref:`th_thiframe`
        * :ref:`th_iframedispatcher`
        
.. _th_introduction:

Introduction
============

    The tableHandler is the Genro way to handle data visualization and data entry.
    
    The tableHandler is structured in two main classes:
    
    * the View class, that allows to manage data visualization
    * the Form class, that allows to manage data entry
    
    These two classes will be visualized respectively into a *view-data window*:
    
    .. image:: ../../images/th/view.png
    
    and into a *data-entry window*:
    
    .. image:: ../../images/th/form.png
    
    For more information of the GUI of these two pages, please check the
    :ref:`genro_view_data` and the :ref:`genro_data_entry` documentation pages.
    
    The tableHandler carries many features:
    
    * You can create your tableHandlers into the ``resources`` folder of your
      :ref:`genro_project`\s. This fact allows to reuse the tableHandlers you created
      in more than a webpage.
      
      Example: if you have to create a table with the registry (in italian , the
      *anagrafica*) of a society, a registry of the staff, a registry of society
      clients (and so on) you can create a single resource that you can reuse every
      time you need it.
      
    * You can choose the GUI of your *data-entry window* from a set of options
      (e.g: dialog, palette, stackcontainer...). Please check the :ref:`th_types`
      section for more information.
      
    In the following sections we try to explain all the info you need to make the new
    tableHandlers works.
    
.. _th_map:

tableHandler paths
==================

    In this section you will learn about the path structure of the tableHandler:
    
    .. image:: ../../images/th/th_map.png
    
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
        
        The ``bottom`` level have an additional ``bar`` level.
      * The ``left`` level allows the user to perform some useful action (e.g: to configurate
        user view; e.g: to export query results in a ``.xls`` file).
      * The ``right`` level is (currently) empty.
      * The ``center`` level is used to create more complex structure inside your page.
        We'll come back later to it, in the :ref:`th_form_center_path` section.
      
    * **record**: at the ``th/form/record`` level, the path of the data is::
    
        .packageName_tableName.form.record
        
      At this path level lie the data of records.
      
      In our example the path will be ``.base_registry.form.record``.
      
      .. warning:: Remember that when you have to interact with data you have to go
                   to the ``form.record`` path.
      
    * **view**: add???
    * **grid**: add???
        
.. _th_firststeps:

first steps
===========

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
    
    .. image:: ../../images/th/th.png
    
    Pay attention that for every tableHandler you want to create, you have to repeat
    the point 3 and 4 of the previous list; for example, if you have three tables called
    ``registry.py``, ``staff.py`` and ``auth.py``, you have to create three folders into the
    ``tables`` folder with a ``th_`` file in each folder, as you can see in the following
    image:
    
    .. image:: ../../images/th/th2.png
    
.. _th_resource_page:

resource webpage
================

    Let's check now the code inside a page with the ``View`` and the ``Form`` classes.
    
    The first line will be::
    
        from gnr.web.gnrbaseclasses import BaseComponent
    
    .. module:: gnr.web.gnrbaseclasses
    
.. _th_view_class:

View class
----------
    
    The ``View`` class is used to let the user visualize some fields of its saved records.
    You don't have to insert ALL the fields of your table, but only the fields that you
    want that user could see in the View.
    
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
        
    (Remember? We explained this line in the :ref:`th_map` section)
    
    The next line can be the :ref:`genro_formbuilder` definition [#]_::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    .. _th_webpage:

th_webpage
==========

    .. note:: when you create a webpage of a :ref:`genro_project` that is related to
              a :ref:`genro_table`, please name it following this convention::
              
                tableName + ``_page.py``
                
              example: if you have a table called ``staff.py``, call the webpage
              ``staff_page.py``.
              
              This convention allows to keep order in your project
              
    When you build some complex tables, you need to use a :ref:`th_resource_page`
    and a ``th_webpage``.
    
    The ``th_webpage`` is a :ref:`webpages_GnrCustomWebPage` that allows you to create
    a much complex :ref:`th_form_class` and that takes the :ref:`th_view_class` from
    its :ref:`th_resource_page` related.
    
    So, if you build a th_webpage, you have to build anyway a :ref:`th_resource_page`
    with the ``View`` class defined in all its structures, while the ``Form`` class
    can be simply::
    
        class Form(BaseComponent):
            def th_form(self, form):
                pass
                
    because you will handle the View class in the th_webpage.
    
    How are the ``th_webpage`` and the :ref:`th_resource_page` related? Through their
    filename. Let's see this fact through an example:
    
        **Example:** let's suppose that you have a project called ``my_project``
        with a package called ``base``. In the package ``base`` there are some
        :ref:`genro_table`\s (``auth.py``, ``invoice.py``, ``registry.py`` and
        ``staff.py``), a :ref:`th_resource_page` (``th_staff.py``) and some
        ``th_webpages`` (``auth_page.py``, ``invoice_page.py`` and ``staff_page.py``):
        
        .. image:: ../../images/th/th_webpages.png
        
        * "staff" is "ok", because we created the table (``staff.py``) in the correct place
          (``base/model``), the :ref:`th_resource_page` in the correct place
          (``base/resources/tables/staff``) with the correct name (``th_`` followed by the
          table name) and the ``th_webpage`` (``staff_page.py`` [#]_) in the correct place
          (``base/webpages``).
          
        * "auth" and "invoice" are "not ok", because there aren't the :ref:`th_resource_page`\s
          called ``th_auth.py`` and ``th_invoice.py``, that are MANDATORIES in order to use the
          ``th_webpages``.
          
    To create your ``th_webpage``, you have to write::
    
        class GnrCustomWebPage(object):
        
    Then you MAY specify the :ref:`genro_table` to which this page refers to::
    
        maintable = 'packageName.tableName'
        
    This line it is not mandatory, because a :ref:`webpages_webpages` (or a ``th_webpage``)
    is related to a table through its :ref:`webpages_maintable` (a :ref:`webpages_variables`)
    or through the :ref:`genro_dbtable` attribute (defined inside one of the
    :ref:`genro_webpage_elements_index`\s). If you define the ``maintable``, then you have
    defined the standard value for all the :ref:`genro_dbtable` attributes of your
    :ref:`genro_webpage_elements_index`\s that support it. Check for more information the
    :ref:`webpages_maintable` and the :ref:`genro_dbtable` documentation pages.
    
.. _th_py_requires:
    
TableHandler py_requires
------------------------

    You have to define the correct :ref:`webpages_py_requires` for your component.
    
    You have two possibilities: because you can use the ``tableHandler`` component as an
    :ref:`components_active` or as a :ref:`components_passive` (We remember that the
    difference is only in the management of the :ref:`webpages_main` method).
    
    **active tableHandler**::
    
        py_requires = 'public:TableHandlerMain'
        
    **passive tableHandler**::
    
        py_requires = 'th/th:TableHandler'
        
.. _th_webpage_methods:
    
th_webpage methods
------------------
    
    Then you may define the following methods (remember to define the :ref:`webpages_main`
    method if you are using the tableHandler as a :ref:`components_passive`)::
        
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
    
    * The ``pageAuthTags``, the ``tableWriteTags`` and the ``tableDeleteTags`` methods
      handle the permits of the page to see it, write on it and delete records. The return
      string (in the example returns ``user``) allow to define who has the permits to act.
      You can find more information on page permits into the :ref:`instanceconfig_authentication`
      section of the :ref:`genro_gnr_instanceconfig` documentation page)
    * The ``windowTitle`` and the ``barTitle`` methods define the title and the bar of the page on the browser.
    
    After that, we have to define the ``th_form`` method; it replaces the ``th_form``
    method we wrote in the :ref:`th_resource_page`.
    
.. _th_webpage_th_form:
    
th_form
-------
    
    The definition line is::
    
        def th_form(self,form,**kwargs):
        
    As we taught to you in the :ref:`th_resource_page` section, the next line is (sometime!)::
    
        pane = form.record
        
    If you need more information on this line, please check the :ref:`th_map` section.
    
    After that, you have to create your :ref:`genro_form`. The next line can be the
    :ref:`genro_formbuilder` definition::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    .. _th_form_center_path:

``center`` path
---------------

    If you need to use some complex :ref:`genro_layout_index` elements in your page, like a
    :ref:`genro_tabcontainer`, you have to pass from the ``form.center`` path. Example::
    
        tc = form.center.tabContainer()
        
        bc = tc.borderContainer(datapath='.record', title='Profilo')
        other = tc.contentPane(title='Other things')
        other.numbertextbox(value='^.number',default=36)
        
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='1px',height='40%')
        top.div('!!Record di anagrafica',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(dbtable='sw_base.anagrafica',margin_left='10px',margin_top='1em',
                             width='370px',datapath='.@anagrafica_id',cols=2)
                             
    .. _th_types:

tableHandler types
==================

    In this section we explain all the tableHandler types. They are a different way to
    show the :ref:`genro_view_data` and the :ref:`genro_data_entry`:
    
    * :ref:`th_border`: show the ``view-data window`` and the ``data-entry window``
      in a single page.
    * :ref:`th_dialog`: show the ``data-entry window`` in a :ref:`genro_dialog` that appears
      over the ``view-data window``.
    * :ref:`th_palette`: show the ``data-entry window`` in a :ref:`genro_palette` that appears
      over the ``view-data window``.
    * :ref:`th_plain`: show only the ``view-data window``. User can't modify records.
    * :ref:`th_stack`: show the ``data-entry window`` and the ``view-data window``
      in two different stack.
      
    They represent a different way to visualize the :ref:`genro_data_entry`,
    where users can add/delete/modify their records. For example, the
    ``dialogTablehandler`` show the *data-entry window* in a dialog that
    will appear over the :ref:`genro_view_data`.
    
.. _types_py_requires:

py_requires
-----------
    
    If you use one of the TableHandler types, it is mandatory to add the following
    :ref:`webpages_py_requires` in your :ref:`webpages_webpages`::
    
        py_requires = 'th/th:TableHandler'
        
    .. _types_common_attributes:
    
common attributes
-----------------

    Some attributes are common to every of these types and we describe those
    attributes here:
    
    * *pane*: add???
    * *nodeId*: the id the tableHandler type. For more information, check the
      :ref:`genro_nodeid` documentation page. Default value is ``None``
    * *table*: the path of the :ref:`genro_table` linked to your tableHandler.
      The syntax is ``table = 'packageName.tableName'``. Default value is ``None``
    
      Example::
      
        table='base.staff'
        
    * *th_pkey*: add???. Default value is ``None``
    * *datapath*: the path of your data. For more information, check the
      :ref:`genro_datapath` documentation page. Default value is ``None``
    * *formResource*: allow to change the default :ref:`th_form_class`.
        Check the :ref:`th_formresource` section for more information.
        Default value is ``None``
    * *viewResource*: allow to change the default :ref:`th_view_class`.
        Check the :ref:`th_viewresource` section for more information.
        Default value is ``None``
    * *formInIframe*: add???. Default value is ``False``
    * *reloader*: add???. Default value is ``None``
    * *readOnly*: boolean. If ``True``, the TableHandler is in read-only mode,
      so user can visualize records and open the :ref:`th_form_class`, but
      he can't add/delete/modify records.
      Default value is ``True`` or ``False`` depending on the widget
      (check it in their method definition).
    * *default_kwargs*: you can add different kwargs:
        
        * *virtualStore*: boolean. add??? Default value is ``False``
        * *relation*: add???. Default value is ``None``.
        * *condition*: add???. Default value is ``None``.
        * *condition_kwargs*: add???. Default value is ``None``.
        * *grid_kwargs*: add???. Default value is ``None``.
        * *hiderMessage*: add???. Default value is ``None``.
        * *pageName*: add???. Default value is ``None``.
        
.. _th_border:

th_borderTableHandler
---------------------

    **Definition:**
    
    .. method:: th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,loadEvent='onSelected',readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,**kwargs)
    
    **Description:**
    
    Based on the Dojo :ref:`genro_bordercontainer`, the borderTableHandler shows the
    :ref:`genro_view_data` and the :ref:`genro_data_entry` in a single page.
    
    .. image:: ../../images/th/border_th.png
    
    **Attributes:**
    
    The attributes that belong to every TableHandler are described in the
    :ref:`types_common_attributes` section. The attributes that belongs only
    to the borderTableHandler are listed here:
    
    * *widget_kwargs*: add???. Default value is ``None``
    * *loadEvent*: add???. Default value is ``'onSelected'``
    * *viewRegion*: add?. Default value is ``None``
    * *formRegion*: add?. Default value is ``None``
    * *vpane_kwargs*: add?. Default value is ``None``
    * *fpane_kwargs*: add?. Default value is ``None``
    
.. _th_dialog:

th_dialogTableHandler
---------------------

    **Definition:**
    
    .. method:: th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,[**kwargs])
    
    **Description:**
    
    The dialogTableHandler shows the :ref:`genro_data_entry` in a dialog over
    the :ref:`genro_view_data`.
    
    .. image:: ../../images/th/dialog_th.png
    
    **attributes:**
    
    The attributes that belong to every TableHandler are described in the
    :ref:`types_common_attributes` section. The attributes that belongs only
    to the dialogTableHandler are listed here:
    
    * *dialog_kwargs*: MANDATORY - define the height and the width of the dialog.
      Default value is ``None``
      
      Example::
      
        dialog_height='100px'; dialog_width='300px'
        
.. _th_palette:

th_paletteTableHandler
----------------------

    **Definition:**
    
    .. method:: th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,palette_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    The paletteTableHandler shows the :ref:`genro_data_entry` in a palette
    over the :ref:`genro_view_data`.
    
    .. image:: ../../images/th/palette_th.png
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`types_common_attributes` section. The attributes that belongs only
    to the paletteTableHandler are listed here:
    
    * *palette_kwargs*: MANDATORY - define the height and the width of the palette.
      Default value is ``None``
      
      Example::
      
        palette_height='100px'; palette_width='300px'
        
.. _th_plain:

th_plainTableHandler
--------------------

    **Definition:**
    
    .. method:: th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=True,**kwargs)
    
    **Description:**
    
    With the plainTableHandler you have only the :ref:`genro_view_data`, so user
    can't modify, add and delete records (infact, the *readOnly* attribute is set
    to ``True``).
    
    .. image:: ../../images/th/plain_th.png
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`types_common_attributes` section. The attributes that belongs only
    to the plainTableHandler are listed here:
    
    * *widget_kwargs*: add???. Default value is ``None``
    
.. _th_stack:

th_stackTableHandler
--------------------

    **Definition:**
    
    .. method:: th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    Based on the Dojo :ref:`genro_stackcontainer`, the stackTableHandler shows the
    :ref:`genro_view_data` and the :ref:`genro_data_entry` in two different pages.
    
    Remembering the Dojo StackContainer definition: *<<A container that has multiple children,*
    *but shows only one child at a time (like looking at the pages in a book one by one).>>*
    
    .. image:: ../../images/th/stack_th.png
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`types_common_attributes` section. The attributes that belongs only
    to the stackTableHandler are listed here:
    
    * *widget_kwargs*: add???. Default value is ``None``
    
.. _th_iframe_types:

iframe types
============
    
    add???
    
    They are:
    
    * :ref:`th_linker`
    * :ref:`th_thIframe`
    * :ref:`th_iframedispatcher`
    
.. _th_linker:

th_linker
---------
    
    **Definition:**
    
    .. method:: th_linker(self,pane,field=None,formResource=None,newRecordOnly=None,openIfNew=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    * *pane*: add???.
    * *field*: add???. Default value is ``None``
    * *formResource*: add???. Default value is ``None``
    * *newRecordOnly*: add???. Default value is ``None``
    * *openIfNew*: add???. Default value is ``None``
    
.. _th_thiframe:

th_thIframe
-----------
    
    **Definition:**
    
    .. method:: th_thIframe(self,pane,method=None,src=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    * *pane*: add???.
    * *method*: add???. Default value is ``None``
    * *src*: add???. Default value is ``None``
    
.. _th_iframedispatcher:

th_iframedispatcher
-------------------
    
    **Definition:**
    
    .. method:: rpc_th_iframedispatcher(self,root,methodname=None,pkey=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    * *root*: add???.
    * *methodname*: add???. Default value is ``None``
    * *pkey*: add???. Default value is ``None``
    
Attributes explanation
======================

.. _th_formresource:

formResource attribute
----------------------

    The formResource attribute allow to choose a modified :ref:`th_form_class` respect
    to the default one. These modified Form classes are structured like the default Form
    class: the difference is that you can call them with the name you want and that
    inside them you can write a different Form class.
    
        **Example:**
        
        This is an example of a Form class inside a :ref:`th_resource_page`::
        
            class Form(BaseComponent):
                def th_form(self, form):
                    pane = form.record
                    fb = pane.formbuilder(cols=2)
                    fb.field('@staff_id.name')
                    fb.field('@staff_id.surname')
                    fb.field('@staff_id.email')
                    fb.field('@staff_id.telephone')
                    fb.field('@staff_id.fiscal_code')
                    
        while this one is the example of a modified Form class::
        
            class MyClass(BaseComponent):
                def th_form(self, form):
                    pane = form.record
                    fb = pane.formbuilder(cols=2)
                    fb.field('@staff_id.name')
                    fb.field('@staff_id.surname')
                    
        In this example the MyClass class allow to write only on two features (name
        and surname) respect to the Form class, in which user can write on more
        fields.
                
    By default your Form class will be taken from the :ref:`th_webpage_th_form` of your
    :ref:`th_webpage` (if it is defined) or from a :ref:`th_resource_page` of your
    resources.
    
    To change the default Form class you have to:
    
    #. create a new Form class (choose the name you want) in a :ref:`th_resource_page`.
    #. use the following syntax in the ``formResource`` attribute::
    
        formResource='fileNameOfYourResource:FormClassName'
        
      where:
      
      * ``fileNameOfYourResource``: the name of your :ref:`th_resource_page`.
        If your file is called ``th_`` followed by the name of the :ref:`genro_table`
        to which your page is related, you can omit to write the
        ``fileNameOfYourResource``, because the standard name is taken automatically.
        Otherwise, write it without its ``.py`` extension.
      * ``FormClassName``: the name you gave to your Form class. You may not write this
        part if the name of your class is the standard one (that is, ``Form``).
        
    **Examples:**
    
    #. If you have a table called ``staff.py``, a resource page called ``th_staff.py``
       with a Form-modified class called ``MyFormClass``, the formResource will be::
       
        formResource=':MyFormClass'
        
       (remember the two dots ``:`` before the class name).
       
       Equally you can write::
       
        formResource='th_staff:MyFormClass'
        
       so you can insert the filename ``th_staff`` or not, because it is the standard
       name.
        
    #. If you have a table called ``staff.py``, a resource page called ``my_great_resource.py``
       with a Form-modified class called ``ThisIsGreat``, the formResource will be::
       
        formResource='my_great_resource:ThisIsGreat'
        
    #. You may call the formResource attibute even if it is not necessary: if you have
       a table called ``staff.py``, a resource page called ``th_staff.py`` and inside it
       the Form class called ``Form``, the formResource will be::
       
        formResource='th_staff:Form'
    
    .. _th_viewresource:

viewResource attribute
----------------------
    
    The viewResource attribute allow to choose a modified :ref:`th_view_class` respect
    to the default one. These modified View classes are structured like the default View
    class: the difference is that you can call them with the name you want and that
    inside them you can write a different View class.
    
        **Example:**
        
        This is an example of a View class inside a :ref:`th_resource_page`::
        
            class View(BaseComponent):
                def th_struct(self,struct):
                    r = struct.view().rows()
                    r.fieldcell('@staff_id.company_name', width='18%')
                    r.fieldcell('@staff_id.telephone', width='6%')
                    r.fieldcell('@staff_id.email', width='12%')
                    r.fieldcell('@staff_id.address',width='12%')
                    r.fieldcell('@staff_id.fax', width='6%')
                    r.fieldcell('@staff_id.www', name='Web site', width='13%')
                    r.fieldcell('@staff_id.notes', width='9%')
                    
        while this one is the example of a modified Form class::
        
            class HelloWorld(BaseComponent):
                def th_struct(self,struct):
                    r = struct.view().rows()
                    r.fieldcell('@staff_id.company_name', width='18%')
                    r.fieldcell('@staff_id.address',width='12%')
                    r.fieldcell('@staff_id.www', name='Web site', width='13%')
                    r.fieldcell('@staff_id.notes', width='9%')
                    
        In this example the HelloWorld class allow to write on a reduced number
        of fields.
        
    By default your :ref:`th_view_class` is defined in the :ref:`th_resource_page`.
    
    To change the default View class you have to:
    
    #. create a new View class (choose the name you want) in a :ref:`th_resource_page`.
    #. use the following syntax in the ``viewResource`` attribute::
    
        viewResource='fileNameOfYourResource:ViewClassName'
        
      where:
      
      * ``fileNameOfYourResource``: the name of your :ref:`th_resource_page`.
        If your file is called ``th_`` followed by the name of the :ref:`genro_table`
        to which your page is related, you can omit to write the
        ``fileNameOfYourResource``, because the standard name is taken automatically.
        Otherwise, write it without its ``.py`` extension.
      * ``ViewClassName``: the name you gave to your modified-View class. You may not
        write this part if the name of your class is the standard one (that is, ``View``).
        
    **Examples:**
    
    #. If you have a table called ``staff.py``, a resource page called ``th_staff.py``
       with a View-modified class called ``MyViewClass``, the viewResource will be::
       
        viewResource=':MyViewClass'
        
       (remember the two dots ``:`` before the class name).
       
       Equally you can write::
       
        viewResource='th_staff:MyViewClass'
        
       so you can insert the filename ``th_staff`` or not, because it is the standard
       name.
        
    #. If you have a table called ``staff.py``, a resource page called ``my_great_resource.py``
       with a View-modified class called ``ThisIsGreat``, the viewResource will be::
       
        viewResource='my_great_resource:ThisIsGreat'
        
    #. You may call the viewResource attibute even if it is not necessary: if you have
       a table called ``staff.py``, a resource page called ``th_staff.py`` and inside it
       the View class called ``Form``, the viewResource will be::
       
        viewResource='th_staff:Form'
        
**Footnotes**:

.. [#] For more information on absolute and relative paths, check the :ref:`genro_datapath` documentation page.
.. [#] The title of the view page is taken from the :ref:`genro_name_long` of the :ref:`genro_table` to which the current webpage refers to.
.. [#] The :ref:`genro_formbuilder` allows to create in a simple way a :ref:`genro_form`. Follow the links for more informations.
.. [#] We remember you that the name of the ``th_webpage`` can be the one you prefer, but as a convention we suggest you to call it with ``name of table`` + ``_page`` suffix.
