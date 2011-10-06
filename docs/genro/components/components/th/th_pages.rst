.. _th_pages:

==================
TableHandler pages
==================

    *Last page update*: |today|
    
    **Creation of a webpage: the "resource webpage" and the "th_webpage"**
    
    * :ref:`th_resource_page`
    * :ref:`th_webpage`
    
        * :ref:`th_resource_page_creation`
        * the :ref:`th_view_class`:
        
            View class methods:
            
            * :ref:`th_condition`
            * :ref:`th_order`
            * :ref:`th_query`
            * :ref:`th_struct`
            
            * the :ref:`th_form_class`:
            
            Form class methods:
            
            * :ref:`th_rpc`
        
        * :ref:`th_webpage_methods`
        * :ref:`th_webpage_th_form`
        * :ref:`th_form_center_path`
        
.. _th_resource_page:

resource webpage
================

    **definition**: A "resource webpage" is a TableHandler page built as a :ref:`resource <intro_resources>`
    
    * the resource webpage is the standard way to build a TableHandler. When you build the
      TableHandler as a resource webpage you have to define its classes:
      
      * the :ref:`th_form_class`
      * the :ref:`th_view_class`
    
    In the next sections we'll see:
    
    * how to create a resource webpage - :ref:`th_resource_page_creation`
    * the complete description of the :ref:`th_form_class` and the :ref:`th_view_class`
      with their methods
      
    The only limit of building the TableHandler as a resource page is that you can't build
    complex :ref:`forms <form>`. For doing this, you have to create a :ref:`th_webpage`
    (we'll come back later on "th_webpages")
    
.. _th_resource_page_creation:

resource webpage - file creation
================================

    .. note:: to create a resource page (and all the necessaries folders) automatically you
              can use the :ref:`gnrmkthresource` script. If you want to create all manually,
              continue to read this section
    
    To create a resource webpage you have to:
    
    #. create a folder called ``resources`` inside the package you are using (in this example
       the package is called ``base``)
    #. Inside the ``resources`` folder just created, create a folder called ``tables``
    #. Inside the ``tables`` folder, create another folder with the SAME name of the
       :ref:`database table <table>` file name: in this example the folder is called
       ``registry``
    #. Inside the ``registry`` folder you have to create a Python file called ``th_``
       + ``tableFileName``: in this example the file is called ``th_registry``
       
    Let's check out this figure that sum up all the creation of new folders and files:
    
        *You should have created all the folders and files highlighted in yellow;*
        *pay attention to call with the same name:*
        
            * *the database table name*
            * *the folder name inside the "tables" folder*
            * *the name of the resource webpage (with the ``th_`` prefix)*
            
        .. image:: ../../../_images/components/th/th.png
    
    Pay attention that for every TableHandler you want to create, you have to repeat
    the point 3 and 4 of the previous list; for example, if you have three tables called
    ``registry.py``, ``staff.py`` and ``auth.py``, you have to create three folders into the
    ``tables`` folder with a ``th_`` file in each folder, as you can see in the following
    image:
    
        .. image:: ../../../_images/components/th/th2.png
    
    .. note:: by default the View and the Form classes will be showned in two different
              pages of a single stack container. In other words, the default TableHandler
              type used will be the :ref:`th_stack`. If you need any other TableHandler
              type, you have to use the :ref:`th_options` method to change this default
              behavior
              
    After you have created the file, you have to insert the :ref:`th_view_class` and a
    :ref:`th_form_class`. For doing this you have to import the ``BaseComponent`` class::
    
        from gnr.web.gnrbaseclasses import BaseComponent
        
    .. _th_webpage:

th_webpage
==========

    When you build some complex tables, you need to use both a :ref:`th_resource_page`
    and a ``th_webpage``.
    
    The ``th_webpage`` is a :ref:`gnrcustomwebpage` that allows you to create
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
    
    How are the ``th_webpage`` and the :ref:`th_resource_page` related through their
    filename. Let's see this fact through an example:
    
        **Example:** let's suppose that you have a project called ``my_project``
        with a package called ``base``. In the package ``base`` there are some
        :ref:`tables <table>` (``auth.py``, ``invoice.py``, ``registry.py`` and
        ``staff.py``), a :ref:`th_resource_page` (``th_staff.py``) and some
        ``th_webpages`` (``auth_page.py``, ``invoice_page.py`` and ``staff_page.py``):
        
            *In the image, the database tables are yellow, the resource webpage*
            *is red and the th_webpages are orange*
            
            .. image:: ../../../_images/components/th/th_webpages.png
        
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
        
    This line it is not mandatory, because a :ref:`webpage` (or a ``th_webpage``)
    is related to a table through its :ref:`maintable` (a :ref:`webpages_variables`)
    or through the :ref:`dbtable` attribute (defined inside one of the :ref:`webpage_elements_index`).
    If you define the ``maintable``, then you have defined the standard value for all the
    :ref:`dbtable` attributes of your :ref:`webpage_elements_index` that support it. Check for more
    information the :ref:`maintable` and the :ref:`dbtable` pages
    
.. _th_webpage_methods:
    
th_webpage methods
------------------
    
    Remember to define the :ref:`webpages_main` method if you are using the
    TableHandler as a :ref:`components_passive`
    
    After that, you have to define the ``th_form`` method; it replaces the ``th_form``
    method we wrote in the :ref:`th_resource_page`
    
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

    If you need to use some :ref:`layout` in your page, like a :ref:`tabcontainer`, you have
    to pass from the ``form.center`` path.
    
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
    
    
.. _th_view_class:

View class
==========
    
    The ``View`` class is used to let the user visualize some fields of its saved records.
    You don't have to insert ALL the fields of your table, but only the fields that you
    want that user could see in the View.
    
    The first line define the class::
    
        class View(BaseComponent):
    
    The methods you may insert are:
    
    * the :ref:`th_condition`
    * the :ref:`th_options`
    * the :ref:`th_order`
    * the :ref:`th_query`
    * the :ref:`th_struct`
    
.. _th_condition:

th_condition
------------

    add???
    
.. _th_order:

th_order
--------
    
    A method of the :ref:`th_view_class`
    
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
    and ``email`` are three rows of a :ref:`table`
    
.. _th_form_class:

Form class
==========
    
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
              to a normal webpage; for more information, check the :ref:`menu_th` section.
              
    .. _th_rpc:

usage of a dataRpc in a resource webpage
----------------------------------------

    In a :ref:`th_resource_page` you can't use a :ref:`datarpc` unless you pass it as a
    callable. For more information, check the :ref:`datarpc_callable` section of the
    :ref:`datarpc` page.