.. _th_further_infos:

====================================
TableHandler: attributes explanation
====================================

    *Last page update*: |today|
    
    * :ref:`th_formresource`
    * :ref:`th_viewresource`
    * :ref:`th_relation_condition`
    
.. _th_formresource:

formResource attribute
======================

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
                
    By default your Form class will be taken from the :ref:`th_form` of your :ref:`th_webpage`
    (if it is defined) or from a :ref:`th_resource_page` of your resources
    
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
      part if the name of your class is the standard one (that is, ``Form``)
      
    **Examples:**
    
    #. If you have a table called ``staff.py``, a resource page called ``th_staff.py``
       with a Form-modified class called ``MyFormClass``, the formResource will be::
       
        formResource=':MyFormClass'
        
       (remember the two dots ``:`` before the class name).
       
       Equally you can write::
       
        formResource='th_staff:MyFormClass'
        
       so you can insert the filename ``th_staff`` or not, because it is the standard
       name
       
    #. If you have a table called ``staff.py``, a resource page called ``my_great_resource.py``
       with a Form-modified class called ``ThisIsGreat``, the formResource will be::
       
        formResource='my_great_resource:ThisIsGreat'
        
    #. You may call the formResource attibute even if it is not necessary: if you have
       a table called ``staff.py``, a resource page called ``th_staff.py`` and inside it
       the Form class called ``Form``, the formResource will be ``formResource='th_staff:Form'``
       
.. _th_viewresource:

viewResource attribute
======================
    
    The viewResource attribute allow to choose a modified :ref:`th_view_class` respect
    to the default one.
    
    The advantage is that you can change the functioning of the View class methods
    
    For example you can:
    
    * change the :ref:`columns` that user see in the :ref:`view_data` through the
      :ref:`th_struct` method
    * modify the base parameters for the query through the :ref:`th_query`
    
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
        
            class MyBeautifulView(BaseComponent):
                def th_struct(self,struct):
                    r = struct.view().rows()
                    r.fieldcell('@staff_id.company_name', width='18%')
                    r.fieldcell('@staff_id.address',width='12%')
                    r.fieldcell('@staff_id.www', name='Web site', width='13%')
                    r.fieldcell('@staff_id.notes', width='9%')
                    
        In this example the "MyBeautifulView" View class allow to show a reduced
        number of :ref:`columns`
        
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
       the View class called ``Form``, the viewResource will be ``viewResource='th_staff:Form'``
       
.. _th_relation_condition:

table, condition and relation attributes
========================================

    A correct setting of a TableHandler needs:
    
    * a *table* parameter: string. Set the :ref:`table` to which the TableHandler is linked.
    * *condition*: the condition gathers the default query parameters, that will be added to the
      optional query made by the user.
      
    Alternatively, if add???, you can specify the *relation* parameter (link the relation parameter
    to the :ref:`relation_name`!!!);
    if you do so, the *table* and the *condition* attributes are taken automatically.
    
    Let's see some examples:
    
        **Example**: *table* and *condition* usage
        
            add???
            
        **Example**: *relation* usage
        
            add???