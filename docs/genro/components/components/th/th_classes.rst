.. _th_classes:

=====================
TableHandler: classes
=====================

    *Last page update*: |today|
    
    * the :ref:`th_view_class`
    
        View class methods:
        
        * :ref:`th_condition`
        * :ref:`th_order`
        * :ref:`th_query`
        * :ref:`th_struct`
        * :ref:`th_layout_methods_view`
        * :ref:`th_options_view`
        
    * the :ref:`th_form_class`
    
        Form class methods:
        
        * :ref:`th_form`
        * :ref:`th_layout_methods_form`
        * :ref:`th_options_form`
        
.. _th_view_class:

View class
==========
    
    The View class is used to let the user visualize saved records. You don't have to insert
    ALL the fields of the table, but only the fields that you want that user could
    see in the :ref:`view_data`
    
    The View Class inherits from the :class:`BaseComponent <gnr.web.gnrbaseclasses.BaseComponent>`
    class, so write::
    
        class View(BaseComponent):
        
    The methods you may use are:
    
    * the :ref:`th_condition`
    * the :ref:`th_order`
    * the :ref:`th_query`
    * the :ref:`th_struct`
    * the :ref:`layout methods <th_layout_methods_view>`
    * the :ref:`th_options <th_options_view>`
    
.. _th_condition:

th_condition
------------

    TODO
    
.. _th_order:

th_order
--------
    
    A :ref:`th_view_class` method
    
    ::
    
        def th_order(self):
            return 'surname'
            
    * The ``th_order`` allows to order the View class alphabetically in relation
      to the field you wrote
    * You can write more than a field; if you do this, the order will follow hierarchically
      the sequence of fields you choose
      
        **Example**::
        
            def th_order(self):
                return 'date,hour'
                
        In this case the records will be ordered following the date order and inside
        the same date following the hour order
    
    * You can optionally specify if the order follows the ascending or the descending way:
        
        * ``:a``: ascending. The records will be showned according to ascending order
        * ``:d``: descending. The records will be showned according to descending order
    
        By default, the ``th_order()`` follows the ascending way (``:a``)
    
        **Example**::
        
            def th_order(self):
                return 'name:d'
                
.. _th_query:

th_query
--------

    A :ref:`th_view_class` method
    
    ::
    
        def th_query(self):
            return dict(column='surname', op='contains', val='', runOnStart=True)
            
    The ``th_query`` defines the default for user to query a database (user can query the
    database from the :ref:`th_gui_view_action_bar` of the :ref:`view_data`).
    
    In particular:
    
    * the ``column`` attribute includes the name of the :ref:`columns` of a :ref:`database
      table <table>`
    * the ``op`` attribute is the SQL operator for SQL queries; for a complete list of the
      operators, check the :ref:`th_query_bar` section
    * the ``val`` attribute is the string to be queried
    * the ``runOnStart=True`` (by default is ``False``) allow to start a query on page loading
      (if you don't write it user have to click the query button to make the query start)
      
.. _th_struct:

th_struct
---------

    A :ref:`th_view_class` method
    
    ::
    
        def th_struct(self,struct):
            r = struct.view().rows()
            r.fieldcell('name', width='12em')
            r.fieldcell('surname', width='12em')
            r.fieldcell('email', width='15em')
            
    This method allow to create the :ref:`grid` with its rows (usually you use some
    :ref:`fieldcell`); in the example above, ``name``, ``surname`` and ``email`` are
    three :ref:`columns` of a :ref:`table`
    
.. _th_layout_methods_view:

layout methods (View class)
---------------------------

    TODO
    
    th_top_*,th_bottom_*,th_left_*,th_right_*
    
.. _th_options_view:

th_options (View class)
-----------------------

    TODO
    
    * excludeDraft(bool)
    * excludeLogicalDeleted(bool)
    * tableRecordCount(bool)
    
.. _th_options:

th_options
----------

    TODO INTEGRARE QUESTO CON th_options(View) e th_options(Form)
    
    It returns a dict to customize your Tablehandler. You can use it both as a method of the
    :ref:`th_view_class` or as a method of the :ref:`th_form_class`
    
    * *dialog_kwargs* use it if you have a :ref:`th_dialog`. There are many options:
    
        * *dialog_height*: MANDATORY - define the dialog height
        * *dialog_width*: MANDATORY - define the dialog width
        * *dialog_title*: define the dialog title
        
        Example::
        
          dialog_height='100px',dialog_width='300px',dialog_title='Customer'
      
    * *formInIframe*: TODO
    * *formResource*: allow to change the default :ref:`th_form_class`
      Check the :ref:`th_formresource` section for more information
    * *fpane_kwargs*: use it if you have a :ref:`th_border`. Allow to set the
      attributes of the :ref:`data_entry`. For the complete list and description
      of the *fpane_kwargs* check the :ref:`th_border` section
    * *lockable*: boolean. TODO
    * *public*: TODO
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
           
    * *vpane_kwargs*: use it if you have a :ref:`th_border`. Allow to set the
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
    
.. _th_form_class:

Form class
==========
    
    The Form class is used to create a :ref:`form` through which user can insert, or modify data.
    
    The Form Class inherits from the :class:`BaseComponent <gnr.web.gnrbaseclasses.BaseComponent>`
    class, so write::
    
        class Form(BaseComponent):
        
    The methods you may use are:
    
    * the :ref:`th_form`
    * the :ref:`layout methods <th_layout_methods_form>`
    * the :ref:`th_options <th_options_form>`
      
.. _th_form:

th_form
-------

    CLIPBOARD::
    
        th_form
        -------
        
            The definition line is::
            
                def th_form(self,form,**kwargs):
                
            If you need to work on data, you need to go at the path ``form.record``::
            
                pane = form.record
                
            if you need more information on this line, please check the :ref:`th_map` page
            
            After that, you have to create your :ref:`form`. Create easily a form
            through a :ref:`formbuilder`::
            
                fb = pane.formbuilder(cols=2, border_spacing='6px')
                
            Then you have to add the columns of the related table that user have to insert;
            for example::
            
                fb.field('name')
                fb.field('surname')
                fb.field('email', colspan=2)
                
    TODO
    
    The first two lines define the class and the method::
    
        NONOOOOOOOO class Form(BaseComponent):
            def th_form(self, form):
            
    Now write the following line::
    
        pane = form.record
        
    (Remember? We explained this line in the :ref:`th_map` section)
    
    The next line can be the :ref:`formbuilder` definition::
    
        fb = pane.formbuilder(cols=2,border_spacing='2px')
        
    In this example we define a formbuilder with two columns (cols=2, default value: 1 column)
    and a margin space between the fields (border_spacing='2px', default value: 6px).
    
    Then you have to add ALL the rows of your table that the user have to compile.
    For example::
    
        fb.field('name')
        fb.field('surname')
        fb.field('email',colspan=2)
        
    .. note:: in the :ref:`packages_menu`, a resource page needs a different syntax respect
              to a normal webpage; for more information, check the :ref:`menu_th` section
              
.. _th_layout_methods_form:

layout methods (Form class)
---------------------------

    TODO
    
    th_top_*,th_bottom_*,th_left_*,th_right_*
    
.. _th_options_form:

th_options (Form class)
-----------------------

    TODO
    
    * linker(bool)
    * lockable(bool)
    * modal(bool)
    * navigation(bool)
    * readOnly(bool)
    * selector(bool)
    * showfooter(bool)
    * showtoolbar(bool)
    