.. _genro_layout_introduction:

================================
 Introduction to the containers
================================

    In Genro you can use layout containers to put panes (or other containers) in specific regions of your page.
    
    There are five regions: top, left, right, bottom and a mandatory center.
    
    As we previously said [#]_, Genro inherit its forms (containers and panes) directly from Dojo.
    
    The containers are:
    
    * the :ref:`genro_bordercontainer`;
    * the :ref:`genro_contentpane`;
    * the :ref:`genro_accordioncontainer`;
    * the :ref:`genro_stackcontainer`;
    * the :ref:`genro_tabcontainer`.
    
    Every container has its children (that are contentPanes). For example, in the accordionContainer you have the accordionPanes.
    
.. _genro_layout_common_attributes:

Common attributes
=================

    There are some common attributes that you can use with all the containers and panes:
    
    * *datapath*: set the root's path of data. Default value is ``None``. For more details, check the :ref:`genro_datapath` page
    * *disabled*: if True, disable the container/pane. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *height*: Set the height of the container. MANDATORY if the container is the father container (example: height='100px')
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *visible*: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page

**Footnotes**

.. [#] We have introduced the containers in the :ref:`genro_webpage-elements-introduction` page.