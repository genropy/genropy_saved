.. _genro_layout_introduction:

===================================
Introduction to the layout elements
===================================
    
    Genro inherits some of its forms (containers and panes) directly from Dojo.
    
    There are also some layout elements built directly through GenroPy.
    
    The containers can be of two types: the Containers and the ContentPanes.
    
    * The containers are able to contain other Containers or ContentPanes.
    * The ContentPanes are able to contain every webpage element, but not a Container.
    
    In Genro you can use the layout containers to put panes (or other containers) in specific regions of your page.
    Every container has its children, that are :ref:`genro_contentpane`\s (For example, the accordionContainer
    has the accordionPanes as its children)
    
.. _genro_layout_widgets:

Genro layout elements
=====================

    The **Genro** layout elements are:
    
    * the :ref:`genro_framepane`
    
.. _dojo_layout_widgets:

Dojo layout elements
====================

    The **Dojo** layout elements are:
    
    * the :ref:`genro_bordercontainer`
    * the :ref:`genro_contentpane`
    * the :ref:`genro_accordioncontainer`
    * the :ref:`genro_splitcontainer`
    * the :ref:`genro_stackcontainer`
    * the :ref:`genro_tabcontainer`
    
.. _genro_layout_common_attributes:

Common attributes
=================

    There are some common attributes that you can use with all the containers and panes:
    
    * *datapath*: set the root's path of data. Default value is ``None``. For more details, check
      the :ref:`genro_datapath` page
    * *disabled*: if True, disable the container/pane. Default value is ``False``. For more information,
      check the :ref:`genro_disabled` documentation page
    * *height*: Set the height of the container. MANDATORY if the container is the father container (example: height='100px')
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`genro_hidden` documentation page
    * *visible*: if False, hide the widget. For more information, check the :ref:`genro_visible` documentation page
    
    You can obviously add :ref:`genro_css` to your containers.
