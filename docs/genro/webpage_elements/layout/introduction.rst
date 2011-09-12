.. _layout_introduction:

===================================
Introduction to the layout elements
===================================
    
    *Last page update*: |today|
    
    Genro inherits some of its forms (containers and panes) directly from Dojo: we call
    them **Dojo layout elements**; they are:
    
    * the :ref:`bordercontainer`
    * the :ref:`contentpane`
    * the :ref:`accordioncontainer`
    * the :ref:`splitcontainer`
    * the :ref:`stackcontainer`
    * the :ref:`tabcontainer`
    
    There are also some layout elements built directly through GenroPy - the **Genro layout elements**:
    
    * the :ref:`framepane`
    
    .. warning:: This is a Dojo rule that works in Genro, too. It is very important that you know it, so
                 we'll tell this rule to you:
                 
                 * A contentPane can include a Container (BorderContainer, TabContainer etc)
                   if and only if it is a UNIQUE child.
                   
.. _layout_common_attributes:

Common attributes
=================

    There are some commons attributes that you can use with all the containers and panes:
    
    * *datapath*: set the root's path of data. Default value is ``None``. For more details, check
      the :ref:`datapath` page
    * *height*: Set the height of the container. MANDATORY if the container is the father container (example: height='100px')
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`hidden` page
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page
    
    You can obviously add :ref:`css` to your containers.
