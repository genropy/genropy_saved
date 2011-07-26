.. _th:

============
TableHandler
============
    
    *Last page update*: |today|
    
    .. note:: summary of the component requirements:
              
              * It is a :ref:`components_standard`.
              * It can be used both as an :ref:`components_active` or as a :ref:`components_passive`:
              
                * :ref:`webpages_py_requires` to use the component as an **active component**::
                  
                      py_requires = 'public:TableHandlerMain'
                      
                * :ref:`webpages_py_requires` to use the component as a **passive component**::
                      
                      py_requires = 'th/th:TableHandler'
                      
    **Introduction, paths, first steps**
    
    * :ref:`th_introduction`
    * :ref:`th_map`:
    
        * :ref:`th_map_selectedpage`
        * :ref:`th_map_form` (:ref:`th_map_form_layout`, :ref:`th_map_form_data`)
        * :ref:`th_map_view`
        
    * :ref:`th_firststeps`
    
    **Creation of a webpage: the "resource webpage" and the "th_webpage"**
    
    * :ref:`th_resource_page`:
    
        * the :ref:`th_view_class` (methods: :ref:`th_struct`, :ref:`th_order` and :ref:`th_query`)
        * the :ref:`th_form_class` (:ref:`th_rpc`)
        
    * :ref:`th_webpage`:
    
        * :ref:`th_webpage_methods`
        * :ref:`th_webpage_th_form`
        * :ref:`th_form_center_path`
        
    **The components**
    
    * :ref:`th_types`:
    
        :ref:`th_common_attributes` - :ref:`th_options`
        
        * :ref:`th_border`
        * :ref:`th_dialog`
        * :ref:`th_page`
        * :ref:`th_palette`
        * :ref:`th_plain`
        * :ref:`th_stack`
        
    * :ref:`th_iframe_types`:
    
        :ref:`th_iframe_common_attributes`
    
        * :ref:`th_thiframe`
        * :ref:`th_iframedialog`
        * :ref:`th_iframedispatcher`
        * :ref:`th_iframepalette`
    
    * :ref:`th_linker_type`:
    
        :ref:`th_linker_common_attributes`
    
        * :ref:`th_linker_base`
        * :ref:`th_linkerbar`
        * :ref:`th_linkerbox`
        
    * :ref:`includedgrid`:
    
        :ref:`ig_attributes`
        
    **Further informations**
    
    * :ref:`th_attr_expl`:
    
        * :ref:`th_formresource`
        * :ref:`th_viewresource`
        * :ref:`th_relation_condition`
        
    **GUI**
        
    * :ref:`th_gui`:
    
        * :ref:`th_query_bar`
    
        
.. _th_introduction:

Introduction
============

    The TableHandler is the Genro way to handle data visualization and data entry.
    
    The TableHandler is structured in two main classes:
    
    * the View class, that allows to manage data visualization
    * the Form class, that allows to manage data entry
    
    These two classes will be visualized respectively into a *view-data window*:
    
    .. image:: ../../_images/components/th/view.png
    
    and into a *data-entry window*:
    
    .. image:: ../../_images/components/th/form.png
    
    For more information of the GUI of these two pages, please check the
    :ref:`view_data` and the :ref:`data_entry` documentation pages.
    
    The TableHandler carries many features:
    
    * You can create your TableHandlers into the ``resources`` folder of your
      :ref:`projects <project>`. This fact allows to reuse the TableHandlers
      you created in more than a webpage.
      
      Example: if you have to create a table with the registry (in italian , the
      *anagrafica*) of a society, a registry of the staff, a registry of society
      clients (and so on) you can create a single resource that you can reuse every
      time you need it.
      
    * You can choose the GUI of your *data-entry window* from a set of options
      (e.g: dialog, palette, stackcontainer...). Please check the :ref:`th_types`
      section for more information.
      
    In the following sections we try to explain all the info you need to make the new
    TableHandlers works.
    
.. _th_map:

TableHandler: paths
===================

    In this section you will learn about the path structure of the TableHandler.
    
    .. note:: you can inspect the path of your data in a webpage directly on your
              browser opening the :ref:`datastore_debugger`.
              
    .. image:: ../../_images/components/th/th_map.png
        
    As any other object in Genro, the TableHandler gathers all the informations through
    a :ref:`bag` structure, that looks like a hierarchiacal and nested structure.
    
    You can access to every level of the structure.
    
    .. warning:: This is important. The root path for the TableHandler data is::
                 
                    packageName_tableName
                    
                 where ``packageName`` is the name of your package and ``tableName`` is
                 the name of your :ref:`table`.
                 
    For example, if the package name is called ``base`` and the table is ``registry.py``,
    the path will be ``.base_registry``.
    
    Nested to it there are the :ref:`th_map_form` level and the :ref:`th_map_view` level
    that handle respectively the path of the data of the :ref:`th_form_class` and
    :ref:`th_view_class`.
    Depending on which :ref:`TableHandler type <th_types>` you will use, there can be also
    the :ref:`th_map_selectedpage` level, that specifies if the selected page is the
    view-data window or the data-entry window.
    
.. _th_map_selectedpage:

selectedPage
------------

    The selectedPage path exists only if you use the :ref:`th_stack`.
    
    The selectedPage contains:
    
    * *form*, if the selected page is the :ref:`view_data`.
    * *view*, if the selected page is the :ref:`data_entry`.
    
.. _th_map_form:

form
----

    This level handles all the data of the :ref:`th_form_class`.
    
    .. image:: ../../_images/components/th/th_map_form.png
    
    It has got two level categories:
    
    * the :ref:`layout levels <th_map_form_layout>`
    * the :ref:`data levels <th_map_form_data>`
    
.. _th_map_form_layout:

form - layout levels
^^^^^^^^^^^^^^^^^^^^
    
    .. image:: ../../_images/components/th/th_map_form_layout.png
    
    At the ``th/form`` level, the path of the data is::
    
        .packageName_tableName.form
        
    The inner gears of the ``form`` level are built in complete analogy with
    the structure of a Dojo :ref:`bordercontainer`, so this level includes
    five region-paths:
    
    * ``top``: it includes the title of the view page [#]_ and the :ref:`workdate`.
    
      (The ``top`` level has a ``bar`` sublevel: this sublevel contains
        some query tools and some buttons to add or delete records.)
    * ``bottom``: it is thought to give to user messages (e.g: 'Save OK').
    
      (The ``bottom`` level have an additional ``bar`` level.)
    * ``left``: it allows the user to perform some useful action (e.g: to configurate
        user view; e.g: to export query results in a ``.xls`` file).
    * ``right``: it is empty.
    * ``center``: it is the space in which you build a GUI to let the user create and
      modify records. We'll come back later to it, in the :ref:`th_form_center_path`
      section.
      
.. _th_map_form_data:

form - data levels
^^^^^^^^^^^^^^^^^^
    
    .. image:: ../../_images/components/th/th_map_form_data.png
    
    In the form level you can find four data levels:
    
    * **controller**: it contains many levels that allow to control the save/load management,
      the incorrect fields and so on (you can check all of them by activating the
      :ref:`datastore_debugger`)
      
      We point up the following levels:
      
      * **invalidFields**: string. If some field is uncorrect (that is, it doesn't satisfy a
          :ref:`validation <validations>`) it contains the path of that field::
          
              packageName_tableName_form_record_columnName
              
          where ``packageName`` is the name of the package, ``tableName`` is the name of the table
          and ``columnName`` is the name of the uncorrect column.
          
      * **table**: string. It includes the name of the package and the name of the table following
        this syntax::
        
            packageName.tableName
            
      * **title**: string. It includes the name of the record title in the :ref:`data_entry`.
      * **valid**: boolean, string. True if every :ref:`validation <validations>` is satisfied.
      
    * **handler**: add???
    * **record**: this level contains all the :ref:`columns <table_column>` of your :ref:`table`.
      
      At the ``th/form/record`` level, the path of the data is::
        
        .packageName_tableName.form.record
        
      .. warning:: at this path level you find the records data, so remember that when you
                   have to interact with data you have to go to the ``form.record`` path.
                   
    * **pkey**: this level contains:
    
        * the ``*newrecord*`` string - if no record is selected;
        * the string with the primary key of the selected record - if a record is selected.
        
.. _th_map_view:

view
----

    .. image:: ../../_images/components/th/th_map_view.png
    
    The view level contains many levels. We point up the following ones:
    
    * **grid**: add???
    * **query**: it contains the parameters of the user queries.
    * **store**: it contains all the records that satisfy the current query.
    * **table**: string. It includes the name of the package and the name of the table
      following this syntax::
        
            packageName.tableName
            
    * **title**: string. It contains the name of the record title in the :ref:`view_data`
    
.. _th_firststeps:

TableHandler: first steps
=========================

    Now we'll guide you in a "step by step" creation of a TableHandler.
    
    Let's suppose that your project is called ``my_project``. Inside the :ref:`packages_model`
    folder we create a table called ``registry.py`` with all the records you need (name,
    surname, email, and so on).
    
    Now, if we have to reuse a lot of time this table - that is, there are a lot of webpages
    that will use this table - we have to create a resource webpage
    
.. _th_resource_page:

resource webpage
================

    To create a resource webpage you have to:
    
    #. create a folder called ``resources`` inside the package we are using (in this example
       the package is called ``base``).
    #. Inside the ``resources`` folder just created, we have to create a folder called ``tables``.
    #. Inside the ``tables`` folder, you have to create another folder with the SAME name of the
       table file name: in this example the folder is called ``registry``
    #. Inside the ``registry`` folder you have to create a Python file called ``th_`` +
       ``tableFileName``: in this example the file is called ``th_registry``
       
    Let's check out this figure that sum up all the creation of new folders and files:
    
    .. image:: ../../_images/components/th/th.png
    
    Pay attention that for every TableHandler you want to create, you have to repeat
    the point 3 and 4 of the previous list; for example, if you have three tables called
    ``registry.py``, ``staff.py`` and ``auth.py``, you have to create three folders into the
    ``tables`` folder with a ``th_`` file in each folder, as you can see in the following
    image:
    
    .. image:: ../../_images/components/th/th2.png
    
    .. note:: by default the View and the Form classes will be showned in two different pages
              of a single stack container. In other words, the default TableHandler type used
              will be the :ref:`th_stack`. If you need any other TableHandler type, you have
              to use the :ref:`th_options` method to change this default behavior.
    
    Let's check now the code inside a resource page.
    
    We have to create a :ref:`th_view_class` and a :ref:`th_form_class`. For doing this
    you have to import the ``BaseComponent`` class::
    
        from gnr.web.gnrbaseclasses import BaseComponent
        
    We introduce now the View class and the Form class.
    
.. _th_view_class:

View class
----------
    
    The ``View`` class is used to let the user visualize some fields of its saved records.
    You don't have to insert ALL the fields of your table, but only the fields that you
    want that user could see in the View.
    
    The first line define the class::
    
        class View(BaseComponent):
    
    The methods you may insert are:
    
    * the :ref:`th_struct`
    * the :ref:`th_order`
    * the :ref:`th_query`.
    
.. _th_struct:

th_struct
---------

    A method of the :ref:`th_view_class`.
    
    ::
    
        def th_struct(self,struct):
            r = struct.view().rows()
            r.fieldcell('name', width='12em')
            r.fieldcell('surname', width='12em')
            r.fieldcell('email', width='15em')
            
    This method allow to create the :ref:`struct` with its rows (usually you
    will use some :ref:`fieldcell`); in the example above, ``name``, ``surname``
    and ``email`` are three rows of a :ref:`table`.
    
.. _th_order:

th_order
--------
    
    A method of the :ref:`th_view_class`.
    
    ::
    
        def th_order(self):
            return 'surname'
            
    * The ``th_order`` allows to order the View class alphabetically in relation
      to the field you wrote.
      
    * You can write more than a field; if you do this, the order will follow hierarchically
      the sequence of fields you choose.
      
        **Example**::
        
            def th_order(self):
                return 'date,hour'
                
        In this case the records will be ordered following the date order and inside
        the same date following the hour order.
    
    * You can optionally specify if the order follows the ascending or the descending way:
        
        * ``:a``: ascending. The records will be showned according to ascending order.
        * ``:d``: descending. The records will be showned according to descending order.
    
        By default, the ``th_order()`` follows the ascending way (``:a``)
    
        **Example**::
        
            def th_order(self):
                return 'name:d'
            
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
    
    The next line can be the :ref:`formbuilder` definition [#]_::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    .. note:: in the :ref:`packages_menu`, a resource page needs a different syntax respect
              to a normal webpage; for more information, check the :ref:`menu_th` documentation
              section.
              
    .. _th_rpc:

usage of a dataRpc in a resource webpage
----------------------------------------

    In a :ref:`th_resource_page` you can't use a :ref:`datarpc` unless you pass it as a
    callable. For more information, check the :ref:`datarpc_callable` section of the
    :ref:`datarpc` documentation page
                      
    .. _th_webpage:

th_webpage
==========

    When you build some complex tables, you need to use both a :ref:`th_resource_page`
    and a ``th_webpage``.
    
    The ``th_webpage`` is a :ref:`webpages_GnrCustomWebPage` that allows you to create
    a much complex :ref:`th_form_class` and that takes the :ref:`th_view_class` from
    its :ref:`th_resource_page` related.
    
    .. note:: when you create a ``th_webpage`` that is related to a :ref:`table`,
              please name it following this convention::
              
                tableName + ``_page.py``
                
              example: if you have a table called ``staff.py``, call the webpage
              ``staff_page.py``.
              
              This convention allows to keep order in your project
    
    So, if you build a ``th_webpage``, you have to build anyway a :ref:`th_resource_page`
    with the ``View`` class defined in all its structures, while the ``Form`` class
    can be simply::
    
        class Form(BaseComponent):
            def th_form(self, form):
                pass
                
    because you will handle the Form class in the th_webpage.
    
    How are the ``th_webpage`` and the :ref:`th_resource_page` related? Through their
    filename. Let's see this fact through an example:
    
        **Example:** let's suppose that you have a project called ``my_project``
        with a package called ``base``. In the package ``base`` there are some
        :ref:`tables <table>` (``auth.py``, ``invoice.py``, ``registry.py`` and
        ``staff.py``), a :ref:`th_resource_page` (``th_staff.py``) and some
        ``th_webpages`` (``auth_page.py``, ``invoice_page.py`` and ``staff_page.py``):
        
        .. image:: ../../_images/components/th/th_webpages.png
        
        * "staff" is "ok", because we created the table (``staff.py``) in the correct place
          (``base/model``), the :ref:`th_resource_page` in the correct place
          (``base/resources/tables/staff``) with the correct name (``th_`` followed by the
          table name) and the ``th_webpage`` (``staff_page.py`` [#]_) in the correct place
          (``base/webpages``).
          
        * "auth" and "invoice" are "not ok", because there aren't the
          :ref:`resource pages <th_resource_page>` called ``th_auth.py`` and ``th_invoice.py``,
          that are MANDATORIES in order to use the ``th_webpages``.
          
    To create your ``th_webpage``, you have to write::
    
        class GnrCustomWebPage(object):
        
    Then you MAY specify the :ref:`table` to which this page refers to::
    
        maintable = 'packageName.tableName'
        
    This line it is not mandatory, because a :ref:`webpages_webpages` (or a ``th_webpage``)
    is related to a table through its :ref:`webpages_maintable` (a :ref:`webpages_variables`)
    or through the :ref:`dbtable` attribute (defined inside one of the
    :ref:`webpage elements <webpage_elements_index>`). If you define the ``maintable``, then you have
    defined the standard value for all the :ref:`dbtable` attributes of your
    :ref:`webpage elements <webpage_elements_index>` that support it. Check for more information the
    :ref:`webpages_maintable` and the :ref:`dbtable` documentation pages.
    
.. _th_webpage_methods:
    
th_webpage methods
------------------
    
    Remember to define the :ref:`webpages_main` method if you are using the
    TableHandler as a :ref:`components_passive`.
    
    After that, you have to define the ``th_form`` method; it replaces the ``th_form``
    method we wrote in the :ref:`th_resource_page`.
    
.. _th_webpage_th_form:
    
th_form
-------
    
    The definition line is::
    
        def th_form(self,form,**kwargs):
        
    As we taught to you in the :ref:`th_resource_page` section, the next line is (sometimes!)::
    
        pane = form.record
        
    If you need more information on this line, please check the :ref:`th_map` section.
    
    After that, you have to create your :ref:`form`. The next line can be the
    :ref:`formbuilder` definition::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (``cols=2``, default value:
    1 column) and a margin space between the fields (``border_spacing='2px'``,
    default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    .. _th_form_center_path:

``center`` path
---------------

    If you need to use some :ref:`layout_index` elements in your page, like a
    :ref:`tabcontainer`, you have to pass from the ``form.center`` path.
    
    **Example**:
    
    ::
    
        tc = form.center.tabContainer()
        
        bc = tc.borderContainer(datapath='.record', title='Profilo')
        other = tc.contentPane(title='Other things')
        other.numbertextbox(value='^.number',default=36)
        
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='1px',height='40%')
        top.div('!!Record di anagrafica',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(dbtable='sw_base.anagrafica',margin_left='10px',margin_top='1em',
                             width='370px',datapath='.@anagrafica_id',cols=2)
                             
    .. _th_types:

TableHandler types
==================

    In this section we explain all the TableHandler types. They are a different way to
    show the :ref:`view_data` and the :ref:`data_entry`:
    
    * :ref:`th_border`: show the ``view-data window`` and the ``data-entry window``
      in a single page.
    * :ref:`th_dialog`: show the ``data-entry window`` in a dialog that appears over the
      ``view-data window``.
    * :ref:`th_palette`: show the ``data-entry window`` in a :ref:`palette` that appears
      over the ``view-data window``.
    * :ref:`th_plain`: show only the ``view-data window``. User can't modify records.
    * :ref:`th_stack`: show the ``data-entry window`` and the ``view-data window``
      in two different stack.
      
    .. _th_common_attributes:
    
TableHandler common attributes
------------------------------

    Some attributes are common to every of these types and we describe those
    attributes here:
    
    * *pane*: MANDATORY - the :ref:`contentpane` to which the TableHandler
      is linked.
      
      .. note:: we suggest you to link a TableHandler to a :ref:`contentpane`;
                avoid a :ref:`bordercontainer`, a :ref:`tabcontainer` or
                other :ref:`layout elements <layout_index>` (if you use them, pay
                attention to use the correct attributes of the layout elements)
      
    * *nodeId*: the id of the TableHandler type. If you don't need a specific nodeId, the component
                handles it automatically. For more information on the meaning of the nodeId, check
                the :ref:`nodeid` documentation page.
    * *table*: the path of the :ref:`table` linked to your TableHandler. It is MANDATORY
      unless you use the relation attribute. For more information, check the
      :ref:`th_relation_condition` example.
      The syntax is ``table = 'packageName.tableName'``.
    
      Example::
      
        table='base.staff'
        
    * *th_pkey*: add???.
    * *datapath*: the path of your data. For more information, check the
      :ref:`datapath` documentation page.
    * *formResource*: allow to change the default :ref:`th_form_class`.
      Check the :ref:`th_formresource` section for more information.
    * *viewResource*: allow to change the default :ref:`th_view_class`.
      Check the :ref:`th_viewresource` section for more information.
    * *formInIframe*: add???.
    * *reloader*: add???.
    * *readOnly*: boolean. If ``True``, the TableHandler is in read-only mode,
      so user can visualize records and open the :ref:`th_form_class`, but
      he can't add/delete/modify records. Default value is ``True`` or ``False``
      depending on the widget (check it in their method definition).
    * *default_kwargs*: you can add different kwargs:
        
        * *virtualStore*: boolean. If it is set to ``True``, it introduces two features:
            
            #. Add the :ref:`th_query_bar` (if it is not yet visualized)
            #. Optimize the time to give the result of a user query: if the user query
               returns a huge set of records as result, the virtualStore load on the client
               only the set of records that user sees in his window, and load more records
               when user scrolls through the result list.
               
        * *relation*: an alternative to the *table* and the *condition* attributes. For more
          information, check the :ref:`th_relation_condition` sections
        * *condition*: MANDATORY unless you specify the relation attribute. Check the
          :ref:`th_relation_condition` section for more information.
        * *condition_kwargs*: the parameters of the condition. Check the
          :ref:`th_relation_condition` section for more information.
        * *grid_kwargs*: add???.
        * *hiderMessage*: add???.
        * *pageName*: add???.
        * *pbl_classes*: if ``True``, allow to use the pbl_roundedgroup and the roundedgrouplabel
          style attributes (of the base CSS theme of Genro) in your TableHandler
          
.. _th_options:

th_options
----------
    
    It returns a dict to customize your Tablehandler. You can use it both as a method of the
    :ref:`th_view_class` or as a method of the :ref:`th_form_class`.
    
    * *DIALOG_KWARGS* add???
    
    * *formInIframe*: add???
    * *formResource*: allow to change the default :ref:`th_form_class`
      Check the :ref:`th_formresource` section for more information
    * *fpane_kwargs*: string. Use it if you have a :ref:`th_border`. Allow to set the
      attributes of the :ref:`data_entry`. For the complete list and description
      of the *fpane_kwargs* check the :ref:`th_border` section
    * *public*: add???
    * *readOnly*: boolean. If ``True``, the element that carries the readOnly attribute is
      in read-only mode
    * *viewResource*: allow to change the default :ref:`th_view_class`
      Check the :ref:`th_viewresource` section for more information
    * *virtualStore*: boolean. If it is set to ``True``, it introduces two features:
          
        #. Add the :ref:`th_query_bar` (if it is not yet visualized)
        #. Optimize the time to give the result of a user query: if the user query
           returns a huge set of records as result, the virtualStore load on the client
           only the set of records that user sees in his window, and load more records
           when user scrolls through the result list
           
    * *vpane_kwargs*: string. Use it if you have a :ref:`th_border`. Allow to set the
      attributes of the :ref:`view_data`. For the complete list and description
      of the *vpane_kwargs* check the :ref:`th_border` section
    * *widget*: string. Specify the TableHandler you want to use. The accepted strings are:
        
        * 'border' for the :ref:`th_border`
        * 'dialog' for the :ref:`th_dialog`
        * 'stack' for the :ref:`th_stack`
        
        **Example**::
        
            class View(BaseComponent):
                def th_options(self):
                    return dict(widget='border',vpane_height='60%')
                    
.. _th_border:

borderTableHandler
------------------

    **Definition:**
    
    .. method:: TableHandler.th_borderTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,loadEvent='onSelected',readOnly=False,viewRegion=None,formRegion=None,vpane_kwargs=None,fpane_kwargs=None,**kwargs)
    
    **Description:**
    
    Based on the Dojo :ref:`bordercontainer`, the borderTableHandler shows the
    :ref:`view_data` and the :ref:`data_entry` in a single page.
    
    .. image:: ../../_images/components/th/border_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.borderTableHandler(...) #not th_borderTableHandler !
    
    **Attributes:**
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the borderTableHandler are listed here:
    
    * *widget_kwargs*: add???
    * *loadEvent*: add???
    * *viewRegion*: add?
    * *formRegion*: add?
    * *vpane_kwargs*: allow to set the attributes of the :ref:`view_data`
      
      In particular, you have the following options:
      
      * *vpane_region*: specify the region occupied by the View class. As for the
        :ref:`bordercontainer`, you may choose between these values: top, left,
        right, bottom, center. By default, the View class has ``vpane_region='top'``
      * *vpane_width* (OR *vpane_height*): specify the width (or the height) occupied
        by the View class (tip: we suggest you to use a percentage, like '30%')
        By default, the View class has ``vpane_height='50%'``
        
      Example::
      
        vpane_region='left',vpane_width='36%'
        
    * *fpane_kwargs*: allow to set the attributes of the :ref:`data_entry`
      
      In particular, you have the following options:
      
      * *fpane_region*: specify the region occupied by the Form class. As for the
        :ref:`bordercontainer`, you may choose between these values: top, left,
        right, bottom, center. By default, the Form class has ``fpane_region='bottom'``
      * *fpane_width*: specify the width occupied by the Form class (tip: we
        suggest you to use a percentage, like '30%') By default, the Form class has
        ``fpane_height='50%'``
      
      Example::

          vpane_region='right',vpane_width='70%'
      
.. _th_dialog:

dialogTableHandler
------------------

    **Definition:**
    
    .. method:: TableHandler.th_dialogTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,dialog_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    The dialogTableHandler shows the :ref:`data_entry` in a dialog over
    the :ref:`view_data`.
    
    .. image:: ../../_images/components/th/dialog_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.dialogTableHandler(...) #not th_dialogTableHandler !
    
    **attributes:**
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the dialogTableHandler are listed here:
    
    * *dialog_kwargs*: there are many options:
    
        * *dialog_height*: MANDATORY - define the dialog height
        * *dialog_width*: MANDATORY - define the dialog width
        * *dialog_title*: define the dialog title
        
      Example::
      
        dialog_height='100px',dialog_width='300px',dialog_title='Customer'
        
.. _th_page:

pageTableHandler
----------------

    **Definition:**
    
    .. method:: TableHandler.th_pageTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,formUrl=None,viewResource=None,formInIframe=False,reloader=None,default_kwargs=None,dbname=None,**kwargs)
    
    **Description:**
    
    The pageTableHandler add???
    
    add??? add image!
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.pageTableHandler(...) #not th_pageTableHandler !
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the pageTableHandler are listed here:
    
    * *formUrl=None*: add???
    
    Example::
    
        add???
    
.. _th_palette:

paletteTableHandler
-------------------

    **Definition:**
    
    .. method:: TableHandler.th_paletteTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,palette_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    The paletteTableHandler shows the :ref:`data_entry` in a palette
    over the :ref:`view_data`.
    
    .. image:: ../../_images/components/th/palette_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.paletteTableHandler(...) #not th_paletteTableHandler !
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the paletteTableHandler are listed here:
    
    * *palette_kwargs*: MANDATORY - define the height and the width of the palette.
      
      Example::
      
        palette_height='100px'; palette_width='300px'
        
.. _th_plain:

plainTableHandler
-----------------

    **Definition:**
    
    .. method:: TableHandler.th_plainTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,reloader=None,readOnly=True,**kwargs)
    
    **Description:**
    
    With the plainTableHandler you have only the :ref:`view_data`. Also, by default
    user can't modify, add and delete records (infact, the *readOnly* attribute is set
    to ``True``). Set it to ``False`` to change this default behavior.
    
    .. image:: ../../_images/components/th/plain_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.plainTableHandler(...) #not th_plainTableHandler !
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the plainTableHandler are listed here:
    
    * *widget_kwargs*: add???.
    
.. _th_stack:

stackTableHandler
-----------------

    **Definition:**
    
    .. method:: TableHandler.th_stackTableHandler(self,pane,nodeId=None,table=None,th_pkey=None,datapath=None,formResource=None,viewResource=None,formInIframe=False,widget_kwargs=None,reloader=None,default_kwargs=None,readOnly=False,**kwargs)
    
    **Description:**
    
    Based on the Dojo :ref:`stackcontainer`, the stackTableHandler shows the
    :ref:`view_data` and the :ref:`data_entry` in two different pages.
    
    Remembering the Dojo StackContainer definition: *<<A container that has multiple children,*
    *but shows only one child at a time (like looking at the pages in a book one by one).>>*
    
    .. image:: ../../_images/components/th/stack_th.png
    
    .. note:: you have to call the TableHandler without the ``th_`` string.
              
              Example::
                    
                    def th_form(self, form):
                        pane = form.center.contentPane()
                        pane.stackTableHandler(...) #not th_stackTableHandler !
    
    **attributes**:
    
    The attributes that belong to every TableHandler are described in the
    :ref:`th_common_attributes` section. The attributes that belongs only
    to the stackTableHandler are listed here:
    
    * *widget_kwargs*: add???.
    
.. _th_iframe_types:

iframe types
============
    
    add???
    
    They are:
    
    * :ref:`th_thiframe`
    * :ref:`th_iframedialog`
    * :ref:`th_iframedispatcher`
    * :ref:`th_iframepalette`
    
.. _th_iframe_common_attributes:

iframe common attributes
------------------------

    Some attributes are common to every of these types and we describe those
attributes here... add???
    
.. _th_thiframe:

thIframe
--------
    
    **Definition:**
    
    .. method:: TableHandler.th_thIframe(self,pane,method=None,src=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    * *pane*: add???.
    * *method*: add???.
    * *src*: add???.
    
.. _th_iframedialog:

IframeDialog
------------

    **Definition:**
    
    .. method:: ThLinker.th_thIframeDialog(self,pane,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    add???
    
.. _th_iframedispatcher:

iframedispatcher
----------------
    
    **Definition:**
    
    .. method:: TableHandler.rpc_th_iframedispatcher(self,root,methodname=None,pkey=None,table=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    * *root*: add???
    * *methodname*: add???
    * *pkey*: add???
    * *table*: add???
    
.. _th_iframepalette:

IframePalette
-------------

    **Definition:**
    
    .. method:: ThLinker.th_thIframePalette(self,pane,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    add???
    
.. _th_linker_type:

linker types
============

    add??? (introduction)
    
    They are:
    
    * :ref:`th_linker_base`
    * :ref:`th_linkerbar`
    * :ref:`th_linkerbox`

.. _th_linker_common_attributes:

linker common attributes
------------------------

    Some attributes are common to every of these types and we describe those
attributes here:

    * *pane*: MANDATORY - the :ref:`contentpane` to which the TableHandler
      is linked.
    * *field*: a :ref:`field`; through this object the linker becomes related to the
      :ref:`table` to which the field belongs to.
    * *newRecordOnly*: add???
    * *dialog_kwargs*: there are many options:
    
        * *dialog_height*: MANDATORY - define the dialog height
        * *dialog_width*: MANDATORY - define the dialog width
        * *dialog_title*: define the dialog title
        
      Example::
      
        dialog_height='100px',dialog_width='300px',dialog_title='Customer'
        
    * *default_kwargs*: add???

.. _th_linker_base:

linker
------

    **Definition:**
    
    .. method:: ThLinker.th_linker(self,pane,field=None,formResource=None,formUrl=None,newRecordOnly=None,table=None,openIfEmpty=None,embedded=True,dialog_kwargs=None,default_kwargs=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    The attributes that belong to every linker are described in the
    :ref:`th_linker_common_attributes` section. The attributes that belongs only
    to the th_linker are listed here:
    
    * *formResource*: allow to change the default :ref:`th_form_class`. Check the
      :ref:`th_formresource` section for more information.
    * *formUrl*: add???
    * *table*: the database :ref:`table` to which the th_linker refers to
    * *openIfEmpty*: add???
    * *embedded*: add???
    
.. _th_linkerbar:

linkerBar
---------

    **Definition:**
    
    .. method:: ThLinker.th_linkerBar(self,pane,field=None,label=None,table=None,_class='pbl_roundedGroupLabel',newRecordOnly=True,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    The attributes that belong to every linker are described in the
    :ref:`th_linker_common_attributes` section. The attributes that belongs only
    to the th_linkerBar are listed here:
    
    * *label*: the label of the linkerBar
    * *table*: the database :ref:`table` to which the th_linkerBar refers to
    * *_class*: the CSS style
    
.. _th_linkerbox:

linkerBox
---------

    **Definition:**
    
    .. method:: ThLinker.th_linkerBox(self,pane,field=None,template='default',frameCode=None,formResource=None,newRecordOnly=None,openIfEmpty=None,_class='pbl_roundedGroup',label=None,**kwargs)
    
    **Description:**
    
    add???
    
    **attributes**:
    
    The attributes that belong to every linker are described in the
    :ref:`th_linker_common_attributes` section. The attributes that belongs only
    to the th_linkerBox are listed here:
    
    * *template*: add???
    * *frameCode*: add???
    * *formResource*: allow to change the default :ref:`th_form_class`. Check the
      :ref:`th_formresource` section for more information.
    * *openIfEmpty*: add???
    * *_class*: the CSS style
    * *label*: the th_linkerBox label
    
        **Example**
        
        add??? example explanation
        
        add??? Explain of the tpl folder --> resources/tables/*TableName*/tpl/default.html
        
        ::
        
            linkerBox('customer_id',
                       dialog_width='300px',dialog_height='260px',dialog_title='Customer',
                       validate_notnull=True,validate_notnull_error='!!Required',
                       newRecordOnly=True,formResource=':MyForm')
                       
.. _includedgrid:

includedGrid
============

    .. method:: add???
    
    lavora come se fosse la visualizzazione di una Bag; nella rappresentazione griglia
    vedi tutte le righe di una Bag, quando editi (dialog oppure inline) (l'editing inline
    è solo della includedGrid). gridEditor serve a modificare la includedGrid.
    
    il "datapath" dell'includedGrid serve solo come retrocompatibilità con l'includedView, quindi come
    path per i dati nell'includedGrid bisogna usare lo "storepath"

    lo storepath può puntare alla Bag (aggiungere anche il datamode='bag'), oppure si può puntare 	ad un path chiocciolinato
    
    
.. _ig_attributes:

includedGrid attributes
-----------------------

    add???

.. _th_attr_expl:

Attributes explanation
======================

    In this section we detail the features of the TableHandler attributes

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
        If your file is called ``th_`` followed by the name of the :ref:`table`
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
        If your file is called ``th_`` followed by the name of the :ref:`table`
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
        
.. _th_relation_condition:

usage of table, condition and relation parameters
-------------------------------------------------

    A correct setting of a TableHandler needs:
    
    * a *table* parameter: string. Set the :ref:`table` to which the TableHandler is linked.
    * *condition*: the condition gathers the default query parameters, that will be added to the
      optional query made by the user.
      
    Alternatively, if add???, you can specify the *relation* parameter;
    if you do so, the *table* and the *condition* attributes are taken automatically.
    
    Let's see some examples:
    
        **Example**: *table* and *condition* usage
        
            add???
            
        **Example**: *relation* usage
        
            add???
    
.. _th_gui:
    
TableHandler GUI
================

    In this section we describe all the pre-set tools user finds in the TableHandler

.. _th_query_bar:
    
query bar
---------

    add???
    
**Footnotes**:

.. [#] The title of the view page is taken from the :ref:`name_long` of the :ref:`table` to which the current webpage refers to.
.. [#] The :ref:`formbuilder` allows to create in a simple way a :ref:`form`. Follow the links for more information.
.. [#] We remember you that the name of the ``th_webpage`` can be the one you prefer, but as a convention we suggest you to call it with ``name of table`` + ``_page`` suffix.
