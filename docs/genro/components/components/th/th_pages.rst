.. _th_pages:

===================
TableHandler: pages
===================

    *Last page update*: |today|
    
    * :ref:`th_pages_intro`
    * :ref:`th_resource_page`
    * :ref:`th_resource_page_creation`
    * :ref:`th_webpage`
    * :ref:`th_relation_pages`
    * :ref:`th_rpc`

.. _th_pages_intro:

introduction
============

    You can build the TableHandler in two different folders of a :ref:`project`:
    
    #. If you build the TableHandler page in the :ref:`"public resources" folder
       <public_resources>`, then the page is called :ref:`th_resource_page`
       
    #. If you build the TableHandler page in the :ref:`"webpages" folder <webpages>`,
       then the page is called :ref:`th_webpage`
       
    This distinction has been thought in order to keep order in your project. Properly,
    you have to think to the "resource webpage" as the standard way to build the
    TableHandler: sometimes you could need only the "resource webpage", sometimes you
    could need of an auxiliary "th_webpage"
    
    .. warning:: Remember that:
                 
                 * the :ref:`th_view_class` can be built **ONLY** in a "resource_webpage"
                 * the :ref:`th_form_class` can be built both in a "resource_webpage" and
                   in a "th_webpage", and you will create a "th_webpage" when you need to
                   build a complex :ref:`th_form_class`: in the next sections
                   (:ref:`th_resource_page` and :ref:`th_webpage`) we investigate this concept
                 * the :ref:`TableHandler "py_requires" <th>` must be defined only in the
                   "th_webpage", not in the "resource webpage"
                   
    *In the image, the "resources" folder (highlighted in yellow), used to keep the "resource webpages"*
    
    .. image:: ../../../_images/projects/packages/resources.png
    
    *In the image, the "webpages" folder (highlighted in yellow), used to keep the "th_webpages"*
    
    .. image:: ../../../_images/projects/packages/webpages.png
    
    In the following sections we introduce the definitions of "resource webpage" and
    "th_webpage" and their features. The complete list of their classes and methods is
    postponed to the :ref:`th_classes` page
    
.. _th_resource_page:

resource webpage
================

    **definition**: A "resource webpage" is a TableHandler page built as a :ref:`resource
    <intro_resources>`
    
    In the next sections we'll see:
    
    * how to create a resource webpage - :ref:`th_resource_page_creation`
    * the complete description of the :ref:`th_form_class` and the :ref:`th_view_class` with
      their methods
      
    As we just say in the :ref:`introduction <th_pages_intro>`, the only limit of building
    the TableHandler as a resource page is that you can't build complex :ref:`forms <form>`.
    For doing this, you have to create a :ref:`th_webpage` (we'll come back later on
    "th_webpages")
    
.. _th_resource_page_creation:

resource webpage creation
=========================

    .. warning:: to create a :ref:`th_resource_page` (and all the necessaries folders)
                 automatically you can use the :ref:`gnrmkthresource` script.
                 
                 If you want to create the file manually, continue to read this section
                 
    To create a resource webpage you have to:
    
    #. create a folder called ``resources`` inside the package you are using (in this example
       the package is called ``base``)
    #. Inside the ``resources`` folder just created, create a folder called ``tables``
    #. Inside the ``tables`` folder, create another folder with the SAME name of the
       :ref:`database table <table>` file name: in this example the folder is called
       ``registry``
    #. Inside the ``registry`` folder you have to create a Python file called ``th_``
       + ``tableFileName``: in this example the file is called ``th_registry``
       
    Let's check out this summary figure:
    
        .. image:: ../../../_images/components/th/th.png
        
    * You should have created all the folders and files highlighted in yellow
    * Pay attention to call with the same name the file highlighted in red, that are:
    
        * the database table name
        * the folder name inside the "tables" folder
        * the name of the resource webpage (with the ``th_`` prefix)
        
    Remember that for every TableHandler you want to create, you have to repeat the points
    3 and 4 of the previous instructions list; for example, if you have three tables called
    ``registry.py``, ``staff.py`` and ``auth.py``, you have to create three folders into the
    ``tables`` folder with a ``th_`` file in each folder, as you can see in the following image:
    
        .. image:: ../../../_images/components/th/th2.png
        
.. _th_webpage:

th_webpage
==========

    **definition**: The "th_webpage" is a :ref:`gnrcustomwebpage` that allows you to create
    a much complex :ref:`th_form_class`: in particular you normally redefine the :ref:`th_form`
    method. For more information, check the :ref:`th_webpage_example` section
    
    .. warning:: You cannot define the :ref:`th_view_class` inside a "th_webpage": the View
                 class must be defined in its :ref:`th_resource_page` related. So, if you build
                 a "th_webpage", you have to build anyway a :ref:`th_resource_page` with the
                 View class defined in all its structures, while the Form class can be simply::
                 
                    class Form(BaseComponent):
                        def th_form(self, form):
                            pass
                            
                 because you will handle the Form class in the th_webpage
                 
    .. note:: to keep order in your project, when you create a ``th_webpage`` please
              name it following this convention::
              
                tableName + ``_page.py``
                
              (**example**: If you have a table called ``staff.py``, call
              ``staff_page.py`` the webpage related)
              
    If you need to use some :ref:`layout` in your page, like a :ref:`tabcontainer`, you have
    to set your layout widgets at the ``form.center`` path (more information in the
    :ref:`following example <th_webpage_example>`)
    
.. _th_webpage_example:

"th_webpage": example
=====================

    We show you an example of a :ref:`th_webpage`; as you can see, the page is a
    the :ref:`gnrcustomwebpage` that contains:
    
    * the correct :ref:`"py_requires" <th>` to call the TableHandler
    * a :ref:`maintable` to define the related :ref:`database table <table>`
    * a redefinition of the :ref:`th_form` method (redefinition because it overwrites the
      "th_form" method of the relative :ref:`th_resource_page`)
    * a custom method to handle the :ref:`form` creation; in particular, it has the
      :ref:`datapath` attribute set to ``.record``, so the :ref:`fields <field>` included
      into the :ref:`formbuilder` have the correct path (``form.record``) for data management
      (more information on paths in the :ref:`th_map` page)
      
      ::
    
        class GnrCustomWebPage(object):
            py_requires = 'public:TableHandlerMain'
            maintable = 'invoice.product'
            
            def th_form(self, form, **kwargs):
                tc = form.center.tabContainer(margin='5px', **kwargs)
                self.productPage(tc.contentPane(title='!!Product', datapath='.record'))
                
            def productPage(self, pane):
                fb = pane.formbuilder(cols=2, lbl_width='7em', fld_width='20em')
                fb.field('code', readOnly=True, width='7em')
                fb.field('description')
                fb.field('price', tag='currencyTextbox', width='7em')
                fb.field('product_type', hasDownArrow=True)
                fb.field('full_description', tag='simpleTextArea', width='100%',
                          height='8ex', colspan=2, lbl_vertical_align='top')
                          
.. _th_relation_pages:

relation between a "th_webpage" and a "resource_webpage"
========================================================

    If you need to use Tablehandler with both a :ref:`th_resource_page` and a :ref:`th_webpage`,
    the component indentify the link between the two pages if they are handled correctly.
    
    In particular:
    
    * for the :ref:`th_resource_page` you have to call the Python file following this syntax::
    
        "th_" + "tableName" + ".py"
        
      where "tableName" is the :ref:`database table <table>` related (e.g: if the table is called
      "invoice", the "resource webpage" must be called "th_invoice.py")
      
    * for the :ref:`th_webpage` you have to define the correct :ref:`maintable` webpage variable
      inside the :ref:`gnrcustomwebpage` class::
    
        class GnrCustomWebPage(object):
            maintable = 'packageName.tableName'
        
      where ``tableName`` is the **same table** specified in the "resource webpage" and
      ``packageName`` is the :ref:`package <packages>` the table belongs to.
      
.. _th_rpc:

usage of a dataRpc in a resource webpage
========================================

    In a :ref:`th_resource_page` you can't use a :ref:`datarpc` unless you pass it as a
    callable. For more information, check the :ref:`datarpc_callable` section of the
    :ref:`datarpc` page
    
**Footnotes**:

.. [#] We remember you that the name of the ``th_webpage`` can be the one you prefer, but as a convention we suggest you to call it with ``name of table`` + ``_page`` suffix