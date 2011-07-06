.. _genro_layout_introduction:

===================================
Introduction to the layout elements
===================================
    
    Genro inherits some of its forms (containers and panes) directly from Dojo: we call
    them **Dojo layout elements**; they are:
    
    * the :ref:`genro_bordercontainer`
    * the :ref:`genro_contentpane`
    * the :ref:`genro_accordioncontainer`
    * the :ref:`genro_splitcontainer`
    * the :ref:`genro_stackcontainer`
    * the :ref:`genro_tabcontainer`
    
    There are also some layout elements built directly through GenroPy - the **Genro layout elements**:
    
    * the :ref:`genro_framepane`
    
    .. warning:: This is a Dojo rule that works in Genro, too. It is very important that you know it, so
                 we'll tell this rule to you:
                 
                 a contentPane can include a BorderContainer or a TabContainer on any other layout
                 element if and only if it is a UNIQUE child.
    
    Lastly, in Genro you can use the layout containers to put panes (or other containers) in specific regions
    of your page. Every container has its children, that are :ref:`genro_contentpane`\s (For example,
    the accordionContainer has the accordionPanes as its children)
    
.. _genro_layout_common_attributes:

Common attributes
=================

    There are some commons attributes that you can use with all the containers and panes:
    
    * *datapath*: set the root's path of data. Default value is ``None``. For more details, check
      the :ref:`genro_datapath` page
    * *height*: Set the height of the container. MANDATORY if the container is the father container (example: height='100px')
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`genro_hidden` documentation page
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page
    
    You can obviously add :ref:`genro_css` to your containers.
